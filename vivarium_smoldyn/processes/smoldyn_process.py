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
            print('species ' + name)
            self.species[name] = self.smoldyn.addSpecies(name, **config)
            # self.set_species(name, dict(config, {
            #     'high': self.parameters['high'],
            #     'low': self.parameters['low']}))

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

        # TODO -- configure surfaces

        if self.parameters['animate']:
            self.smoldyn.addGraphics("opengl")

    def set_species(self, name, config):
        self.smoldyn.runCommand(f"killmol {name}")
        self.species[name].addToSolution(
            config.get('counts'),
            highpos=config.get('high'),
            lowpos=config.get('low'))

    def set_state(self, state):
        for name, config in state.items():
            self.set_species(name, config)

    def ports_schema(self):
        return {
            # TODO -- molecules have counts OR locations. make this optional
            'molecules': {
                mol_id: {
                    '_default': 0,
                    '_updater': 'accumulate',
                    '_emit': True,
                } for mol_id in self.parameters['species'].keys()
            },
            # TODO -- effective rates (as a result of crowding) could be optional
            'effective_rates': {}
        }

    def next_update(
            self,
            timestep,
            states
    ):

        # TODO: take the state, and use it to configure smoldyn

        for name, counts in states['molecules'].items():
            self.set_species(
                name, {
                    'counts': counts,
                    'high': self.parameters['high'],
                    'low': self.parameters['low']
                }
            )

        self.smoldyn.run(
            stop=timestep,
            dt=self.dt)

        # get the data, clear the buffer
        data = self.smoldyn.getOutputData('counts', True)
        final_counts = data[-1]

        # TODO -- post processing to get effective rates

        molecules = {}
        for index, name in enumerate(self.parameters['species'].keys(), 1):
            molecules[name] = final_counts[index] - states['molecules'][name]

        import ipdb; ipdb.set_trace()

        return {
            'molecules': molecules,
            'effective_rates': {},
        }


# functions to configure and run the process
def test_smoldyn_process(
        animate=False
):
    # initialize the process by passing in parameters
    parameters = {
        'animate': animate,
        'species': {
            'X': {'difc': 0, 'color': 'green', 'display_size': 3},
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

    import ipdb; ipdb.set_trace()

    template_process = SmoldynProcess(parameters)


    # declare the initial state
    initial_state = {
        'molecules': {
            'X': 10
        }
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
