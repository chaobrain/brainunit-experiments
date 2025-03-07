# Copyright 2024 BDP Ecosystem Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import brainunit as u
from diffrax import diffeqsolve, ODETerm, SaveAt, Dopri5

k = 0.2 / u.ms
ode = lambda t, y, args: -k * y

y0 = 0.50 * u.molar
t0 = 0 * u.ms
t1 = 10 * u.ms
sol = diffeqsolve(
    ODETerm(ode), Dopri5(), t0=t0, t1=t1, dt0=0.01 * u.ms, y0=y0,
    saveat=SaveAt(ts=u.math.linspace(t0, t1, 100), t1=True, t0=True)
)
