# Copyright 2025 BDP Ecosystem Limited. All Rights Reserved.
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

import braintools as bts
import jax
import matplotlib.pyplot as plt
import numpy as np
import pint
import pint as u

dtype = np.float64
duration = 50


def astype(x):
    if isinstance(x, u.Quantity):
        return x.astype(dtype)
    else:
        return np.asarray(x).astype(dtype)


# x（对流速度）: m/s
# y（温度）: K
# z（垂直温度梯度）: K/m

ureg = pint.UnitRegistry()
unit_of_x = ureg.meter / ureg.second
unit_of_y = ureg.kelvin
unit_of_z = ureg.kelvin
# unit_of_t = ureg.msecond
unit_of_t = ureg.second


# Define the Lorenz system differential equations
def lorenz_with_unit(
    t,
    state,
    sigma=astype(10.0 / unit_of_t),
    rho=astype(28.0 * unit_of_z),
    beta=astype(8 / 3 / unit_of_t)
):
    x, y, z = state
    dxdt = sigma * (y / unit_of_y * unit_of_x - x)
    dydt = (x * (rho - z) / unit_of_z / unit_of_x * unit_of_y - y) / unit_of_t
    dzdt = x * y / unit_of_x / unit_of_y * unit_of_z / unit_of_t - beta * z
    return [dxdt, dydt, dzdt]


# Define the Lorenz system differential equations
def lorenz_without_unit(
    t,
    state,
    sigma=astype(10.0),
    rho=astype(28.0),
    beta=astype(8 / 3)
):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]


# Initial conditions
initial_state1 = [astype(1.0 * unit_of_x),
                  astype(1.0 * unit_of_y),
                  astype(1.0 * unit_of_z)]
# Introduce a very small perturbation in the initial x-coordinate
initial_state2 = [astype(1.0), astype(1.0), astype(1.0)]


def rk4(f, t, y, h):
    k1 = jax.tree.map(lambda x: h * x, f(t, y))
    k2 = jax.tree.map(lambda x: h * x, f(t + h / 2, jax.tree.map(lambda x, y: x + y / 2, y, k1)))
    k3 = jax.tree.map(lambda x: h * x, f(t + h / 2, jax.tree.map(lambda x, y: x + y / 2, y, k2)))
    k4 = jax.tree.map(lambda x: h * x, f(t + h, jax.tree.map(lambda x, y: x + y, y, k3)))
    return jax.tree.map(
        lambda x, k1, k2, k3, k4: x + (k1 + 2 * k2 + 2 * k3 + k4) / 6,
        y, k1, k2, k3, k4
    )


def solve_ivp(fun, t0, t1, dt, y0):
    t = t0
    y = y0
    ys = jax.tree.map(lambda x: np.array([x.magnitude if isinstance(x, u.Quantity) else x]), y)
    times = [t]
    while t < t1:
        y = rk4(fun, t, y, dt)
        t = t + dt
        ys = jax.tree.map(
            lambda x, y: np.concatenate([x, np.asarray([y.magnitude if isinstance(y, u.Quantity) else y])]),
            ys, y
        )
        # print(t, dt)
        times.append(t)
    return times, ys, y
    return np.asarray(times), ys, y


# Solve the Lorenz system for both initial conditions
times, sol1, _ = solve_ivp(
    lorenz_with_unit,
    0 * unit_of_t,
    duration * unit_of_t,
    astype(0.01 * unit_of_t),
    initial_state1
)
times, sol2, _ = solve_ivp(
    lorenz_without_unit,
    0,
    duration,
    astype(0.01),
    initial_state2
)
sol1 = np.asarray(sol1)
sol2 = np.asarray(sol2)
times = times

# Plot the results
fig, gs = bts.visualize.get_figure(5, 1, 1.5, 4.5)

# Left Plot: 3D Trajectories
ax1 = fig.add_subplot(gs[:4], projection='3d')
ax1.plot(sol1[0], sol1[1], sol1[2], label='With Pint', color='blue')
ax1.plot(sol2[0], sol2[1], sol2[2], label='Without Pint', color='red', alpha=0.7)
ax1.set_title('3D Trajectories of the Lorenz System')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.legend()

# Right Plot: Distance Over Time
# Calculate the Euclidean distance between the two solutions at each time point
distance = np.linalg.norm(sol1 - sol2, axis=0)

ax2 = fig.add_subplot(gs[4])
ax2.plot(times, distance, color='green')
# ax2.set_yscale('log')  # Use logarithmic scale to clearly show exponential growth
ax2.set_title('Distance Between Trajectories Over Time')
ax2.set_xlabel('Time t')
ax2.set_ylabel('Distance')
ax2.set_xlim(0, duration)
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')

plt.savefig(f'results/lorenz_en_pint-{dtype.__name__}.pdf')
plt.savefig(f'results/lorenz_en_pint-{dtype.__name__}.eps')

# plt.show()
