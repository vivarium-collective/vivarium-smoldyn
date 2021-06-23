"""
Smoldyn

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


class Smoldyn(Process):
    """ Smoldyn Process

    A spatial stochastic simulator for chemical reaction networks

    http://www.smoldyn.org/index.html

    TODO: suppress print out
    """

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
        self.simulation = sm.Simulation(
            low=self.parameters['low'],
            high=self.parameters['high'],
            types=self.parameters['boundary'],
        )
        self.simulation.addOutputData('counts')
        self.simulation.addCommand(cmd='molcount counts', cmd_type='E')

        # make the species
        self.species = {}
        for name, config in self.parameters['species'].items():
            print('species ' + name)
            self.species[name] = self.simulation.addSpecies(name, **config)

        # make the reactions
        self.reactions = {}
        for rxn_name, config in self.parameters['reactions'].items():
            substrate_names = config.pop('subs')
            product_names = config.pop('prds')
            substrates = [self.species[name] for name in substrate_names]
            products = [self.species[name] for name in product_names]
            self.reactions[rxn_name] = self.simulation.addReaction(
                rxn_name,
                subs=substrates,
                prds=products,
                **config)

        # TODO -- configure surfaces

        if self.parameters['animate']:
            self.simulation.addGraphics('opengl')

    def set_uniform(self, name, config):
        self.simulation.runCommand(f'killmol {name}')
        self.species[name].addToSolution(
            config.get('counts'),
            highpos=config.get('high'),
            lowpos=config.get('low'))

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
            # TODO -- effective rates (as a result of crowding). could be optional
            'effective_rates': {}
        }

    def next_update(
            self,
            timestep,
            states
    ):

        # reset the molecules, at a uniform distribution
        for name, counts in states['molecules'].items():
            self.set_uniform(
                name, {
                    'counts': counts,
                    'high': self.parameters['high'],
                    'low': self.parameters['low']})

        # run simulation
        self.simulation.run(
            stop=timestep,
            dt=self.dt)

        # get the data, clear the buffer
        data = self.simulation.getOutputData('counts', True)

        # get the final counts for the update
        final_counts = data[-1]
        molecules = {}
        for index, name in enumerate(self.parameters['species'].keys(), 1):
            molecules[name] = int(final_counts[index]) - states['molecules'][name]

        # TODO -- post processing to get effective rates

        return {
            'molecules': molecules,
            # 'effective_rates': {},
        }


# functions to configure and run the process
def test_smoldyn_process(
        animate=False
):
    # initialize the process by passing in parameters
    parameters = {
        'animate': animate,
        'species': {
            'X': {'difc': 0},
            'A': {'difc': 1},
            'B': {'difc': 1},
            'A2': {'difc': 1},
            'B2': {'difc': 1}},
        'reactions': {
            'express': {
                'subs': ['X'],
                'prds': ['X', 'A', 'B'],
                'rate': 1},
            'Adimer': {
                'subs': ['A', 'A'],
                'prds': ['A2'],
                'rate': 1},
            'Adimer_reverse': {
                'subs': ['A2'],
                'prds': ['A', 'A'],
                'rate': 1},
            'Bdimer': {
                'subs': ['B', 'B'],
                'prds': ['B2'],
                'rate': 1},
            'Bdimer_reverse': {
                'subs': ['B2'],
                'prds': ['B', 'B'],
                'rate': 1},
            'AxB': {
                'subs': ['A2', 'B'],
                'prds': ['A2'],
                'rate': 1},
            'Adegrade': {
                'subs': ['A'],
                'prds': [],
                'rate': 1},
            'Bdegrade': {
                'subs': ['B'],
                'prds': [],
                'rate': 1}}}

    process = Smoldyn(parameters)

    # declare the initial state
    initial_state = {
        'molecules': {
            'X': 10}}

    # run the simulation
    sim_settings = {
        'total_time': 100,
        'initial_state': initial_state}
    output = simulate_process(
        process,
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
