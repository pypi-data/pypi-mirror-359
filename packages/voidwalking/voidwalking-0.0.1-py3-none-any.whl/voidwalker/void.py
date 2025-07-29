import torch

class Voidwalker:
    def __init__(self, points, n_samples, n_voids, bounds, margin=10, initial_radius=1e-2, growth_step=1e-2, max_radius=None,
                 move_step=1e-1, max_steps=25_000, max_failures=10, outer_ring_width=10.0, alpha=0.05, record_frames=False):
        self.points = points
        self.n_voids = n_voids
        self.n_samples = n_samples

        if not isinstance(bounds, torch.Tensor):
            bounds = torch.tensor(bounds, dtype=torch.float32)
        self.bounds = bounds

        self.margin = margin
        self.growth_step = growth_step
        self.move_step = move_step
        self.max_steps = max_steps
        self.max_failures = max_failures
        self.max_radius = max_radius
        self.initial_radius = initial_radius
        self.outer_ring_width = outer_ring_width
        self.alpha = alpha

        self.d = points.shape[1]
        self.voids = self._initialise_voids()
        self.active = torch.ones(n_voids, dtype=torch.bool)
        self.consec_failures = torch.zeros(n_voids, dtype=torch.int)

        self.record_frames = record_frames
        self.frames = []

        area = torch.prod(self.bounds[:, 1] - self.bounds[:, 0])
        self.global_density = self.points.shape[0] / area

    def _record_frame(self):
        if self.record_frames:
            centres = self.voids[:, :self.d].clone()
            radii = self.voids[:, self.d].clone()
            self.frames.append((centres, radii))

    def _initialise_voids(self):
        d = self.points.shape[1]
        candidates = torch.rand(self.n_samples, d) * (self.bounds[:, 1] - self.bounds[:, 0]) + self.bounds[:, 0]
        dists = torch.cdist(candidates, self.points)
        min_dists_to_points = dists.min(dim=1).values
        safe = min_dists_to_points > (self.initial_radius + self.margin)
        candidates = candidates[safe]
        scores = min_dists_to_points[safe]

        if len(candidates) < self.n_voids:
            raise RuntimeError("Not enough valid initial voids after filtering.")

        selected = [candidates[scores.argmax().item()]]
        mask = torch.ones(len(candidates), dtype=torch.bool)
        mask[scores.argmax().item()] = False
        candidates = candidates[mask]

        for _ in range(1, self.n_voids):
            dists = torch.cdist(candidates, torch.stack(selected))
            min_dists = dists.min(dim=1).values
            selected.append(candidates[min_dists.argmax().item()])
            candidates = torch.cat([candidates[:min_dists.argmax().item()], candidates[min_dists.argmax().item() + 1:]])
            if len(candidates) == 0:
                break

        if len(selected) < self.n_voids:
            raise RuntimeError("Failed to seed enough voids after maximin filtering.")

        centres = torch.stack(selected)
        radii = torch.full((self.n_voids, 1), self.initial_radius)
        return torch.cat([centres, radii], dim=1)

    def get_outer_ring_membership(self):
        centres = self.voids[:, :self.d]
        radii = self.voids[:, self.d]
        dists = torch.cdist(self.points, centres)
        inner_bounds = radii.unsqueeze(0)
        outer_bounds = (radii + self.outer_ring_width).unsqueeze(0)
        within_outer_ring = (dists > inner_bounds) & (dists <= outer_bounds)
        memberships = [torch.where(within_outer_ring[:, i])[0] for i in range(self.n_voids)]
        return memberships

    def _point_distances(self, centres):
        return torch.cdist(centres, self.points)

    def _sample_directions(self):
        dirs = torch.randn(self.n_voids, self.d)
        return dirs / dirs.norm(dim=1, keepdim=True)

    def _can_grow_mask(self):
        centres = self.voids[:, :self.d]
        current_radii = self.voids[:, self.d:self.d + 1]
        proposed_radii = current_radii + self.growth_step
        dists = self._point_distances(centres)
        min_dists = dists.min(dim=1, keepdim=True).values
        safe_from_points = min_dists > proposed_radii + self.margin

        if self.max_radius is not None:
            under_max = proposed_radii <= self.max_radius
            return (safe_from_points & under_max).squeeze()
        else:
            return safe_from_points.squeeze()

    def _can_move(self, new_centres):
        dists = torch.cdist(new_centres, self.points)
        radii = self.voids[:, self.d:self.d + 1]
        min_dists = dists.min(dim=1, keepdim=True).values
        lower = self.bounds[:, 0].unsqueeze(0)
        upper = self.bounds[:, 1].unsqueeze(0)
        within_bounds = (new_centres >= lower) & (new_centres <= upper)
        in_bounds_mask = within_bounds.all(dim=1)
        dist_check = (min_dists > radii + self.margin).squeeze()
        return (dist_check & in_bounds_mask) & self.active

    def _attempt_walk(self, mask=None):
        if mask is None:
            mask = self.active

        centres = self.voids[:, :self.d]
        radii = self.voids[:, self.d:self.d + 1]
        vp_dists = torch.cdist(centres, self.points)
        vp_overlap = vp_dists < (radii + self.margin)
        vv_dists = torch.cdist(centres, centres)
        rr_sum = radii + radii.T + self.margin
        vv_overlap = (vv_dists < rr_sum) & (~torch.eye(self.n_voids, dtype=torch.bool))
        repulsion_vecs = torch.zeros_like(centres)

        for i in range(self.n_voids):
            if not mask[i]:
                continue
            repulsion = torch.zeros(self.d)
            overlapping_points = vp_overlap[i]
            if overlapping_points.any():
                offending_points = self.points[overlapping_points]
                dirs = centres[i] - offending_points
                norms = dirs.norm(dim=1, keepdim=True) + 1e-8
                repulsion += (dirs / norms).sum(dim=0)
            overlapping_voids = vv_overlap[i]
            if overlapping_voids.any():
                offending_centres = centres[overlapping_voids]
                dirs = centres[i] - offending_centres
                norms = dirs.norm(dim=1, keepdim=True) + 1e-8
                repulsion += (dirs / norms).sum(dim=0)
            if repulsion.norm() > 0:
                repulsion_vecs[i] = repulsion / repulsion.norm()
            else:
                random_dir = torch.randn(self.d)
                repulsion_vecs[i] = random_dir / random_dir.norm()

        step = self.move_step * repulsion_vecs
        new_centres = centres + step
        new_centres = torch.where(mask.unsqueeze(1), new_centres, centres)
        can_move = self._can_move(new_centres)
        self.voids[can_move, :self.d] = new_centres[can_move]

    def _attempt_grow(self):
        memberships = self.get_outer_ring_membership()
        member_counts = torch.tensor([len(m) for m in memberships], dtype=torch.float32)

        radii = self.voids[:, self.d]
        expected_counts = self.global_density * torch.pi * (
            (radii + self.outer_ring_width) ** 2 - radii ** 2
        )

        # Poisson CDF using lower incomplete gamma: P(N <= k) = gammainc(k+1, lambda)
        # Terminate if P(N >= observed) <= alpha, equivalent to: 1 - P(N <= observed - 1) <= alpha
        k = member_counts.floor()
        lam = expected_counts.clamp(min=1e-8)  # Avoid zeros
        cdf = torch.special.gammainc(k + 1, lam)
        p_values = 1.0 - cdf
        terminate_mask = (p_values <= self.alpha) & self.active

        can_grow = self._can_grow_mask() & self.active & (~terminate_mask)
        self.voids[can_grow, self.d] += self.growth_step
        self.consec_failures[can_grow] = 0

        failed_to_grow = (~can_grow) & self.active & (~terminate_mask)
        self.consec_failures[failed_to_grow] += 1

        if failed_to_grow.any():
            self._attempt_walk(mask=failed_to_grow)

        self.active = self.active & (self.consec_failures < self.max_failures) & (~terminate_mask)
        self._record_frame()

    def run(self):
        for _ in range(self.max_steps):
            if not self.active.any():
                break
            self._attempt_grow()

        centres = self.voids[:, :self.d]
        radii = self.voids[:, self.d:self.d + 1]
        dists = torch.cdist(centres, self.points)
        safe = dists > (radii + self.margin)
        assert torch.all(safe), "One or more voids violate the margin constraint from points."

        return self.voids, radii.squeeze()

def run_voidwalker(points, **kwargs):
    vw = Voidwalker(points, **kwargs)
    voids, radii = vw.run()
    return voids, radii, vw.frames if vw.record_frames else None
