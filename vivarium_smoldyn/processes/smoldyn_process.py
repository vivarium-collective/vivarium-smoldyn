"""
Execute by running: ``python vivarium_smoldyn/processes/smoldyn_process.py``
"""

import os

import smoldyn as sm

from vivarium.core.process import Process
from vivarium.core.composition import (
    simulate_process,
    PROCESS_OUT_DIR,
)
from vivarium.plots.simulation_output import plot_simulation_output


class SmoldynProcess(Process):

    defaults = {
        'animate': False,
        'time_step': 10,
        'low': [0, 0],
        'high': [10, 10],
        'boundary': 'p',
        'dt': 0.1,
        'species': {},
        'reactions': {},
    }

    def __init__(self, parameters=None):
        super().__init__(parameters)

        self.dt = self.parameters['dt']

        # initialize the simulation
        self.smoldyn = sm.Simulation(
            low=self.parameters['low'],
            high=self.parameters['high'],
            types=self.parameters['boundary'],
        )
        self.smoldyn.addOutputData('counts')
        self.smoldyn.addCommand(cmd='molcount counts', cmd_type='E')

        # make the species
        self.species = {}
        for name, config in self.parameters['species'].items():
            solution = None
            if 'solution' in config:
                solution = config.pop('solution')
            self.species[name] = self.smoldyn.addSpecies(name, **config)
            if solution:
                self.species[name].addToSolution(
                    solution.get('counts'),
                    pos=solution.get('position')
            )

        self.reactions = {}
        for rxn_name, config in self.parameters['reactions'].items():
            substrate_names = config.pop('subs')
            product_names = config.pop('prds')
            substrates = [self.species[name] for name in substrate_names]
            products = [self.species[name] for name in product_names]
            self.reactions[rxn_name] = self.smoldyn.addReaction(
                rxn_name,
                subs=substrates,
                prds=products,
                **config
            )

        if self.parameters['animate']:
            self.smoldyn.addGraphics("opengl")

    def ports_schema(self):
        return {
            'internal': {
                'A': {
                    '_default': 1.0,
                    '_updater': 'accumulate',
                    '_emit': True,
                },
            },
        }

    def next_update(
            self,
            timestep,
            states
    ):
        self.smoldyn.run(
            stop=timestep,
            dt=self.dt)

        # get the data, clear the buffer
        data = self.smoldyn.getOutputData('counts', True)
        final_counts = data[-1]
        import ipdb;
        ipdb.set_trace()

        return {}


# functions to configure and run the process
def test_smoldyn_process(
        animate=False
):
    # initialize the process by passing in parameters
    parameters = {
        'animate': animate,
        'species': {
            'X': {'difc': 0, 'color': 'green', 'display_size': 3, 'solution': {'counts': 1, 'position': [5, 5]}},
            'A': {'difc': 1, 'color': 'red', 'display_size': 3},
            'B': {'difc': 1, 'color': 'blue', 'display_size': 3},
            'A2': {'difc': 1, 'color': 'red', 'display_size': 5},
            'B2': {'difc': 1, 'color': 'blue', 'display_size': 5},
        },
        'reactions': {
            'express': {'subs': ['X'], 'prds': ['X', 'A', 'B'], 'rate': 1},
            'Adimer': {'subs': ['A', 'A'], 'prds': ['A2'], 'rate': 1},
            'Adimer_reverse': {'subs': ['A2'], 'prds': ['A', 'A'], 'rate': 1},
            'Bdimer': {'subs': ['B', 'B'], 'prds': ['B2'], 'rate': 1},
            'Bdimer_reverse': {'subs': ['B2'], 'prds': ['B', 'B'], 'rate': 1},
            'AxB': {'subs': ['A2', 'B'], 'prds': ['A2'], 'rate': 1},
            'Adegrade': {'subs': ['A'], 'prds': [], 'rate': 1},
            'Bdegrade': {'subs': ['B'], 'prds': [], 'rate': 1},
        },
    }
    template_process = SmoldynProcess(parameters)

    # declare the initial state
    initial_state = {
        'internal': {
            'A': 0.0
        },
        'external': {
            'A': 1.0
        },
    }

    # run the simulation
    sim_settings = {
        'total_time': 100,
        'initial_state': initial_state}
    output = simulate_process(
        template_process,
        sim_settings)

    return output


def main():
    out_dir = os.path.join(PROCESS_OUT_DIR, 'smoldyn')
    os.makedirs(out_dir, exist_ok=True)

    output = test_smoldyn_process(animate=False)

    # plot the simulation output
    plot_settings = {}
    plot_simulation_output(
        output,
        plot_settings,
        out_dir)


if __name__ == '__main__':
    main()
