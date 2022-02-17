from turtle import width
import pandas as pd
import numpy as np
from random import normalvariate, random
import plotly.express as px

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from cadCAD.engine import ExecutionContext, Executor
from cadCAD import configs
import streamlit as st


# Additional dependencies

# For analytics
import numpy as np
# For visualization
import plotly.express as px
pd.options.plotting.backend = "plotly"

st.header('CeSci Value Flow Model')

def p_value_flow(params, substep, state_history, previous_state):
    funding = 0
    management_costs = 0
    to_researcher = 0
    to_journal = 0
    salary = 0
    losses = 0
    if random() < params['probability_funding'] and (previous_state['funding_pool'] > funding):
        funding = params['funding_round']
        management_costs = funding * params['alpha']
        to_researcher = funding - management_costs
        losses = management_costs

        research_value = funding * (1-params['epsilon'])
        losses += to_researcher - research_value

        salary = research_value * params['beta']
        to_journal = research_value + params['cost_publishing']
        if random() < params['probability_buying']:
            salary = salary - params['cost_buying']
            to_journal += params['cost_buying']
    # losses = funding - to_journal
    return {'update_researcher_funding': to_researcher,
            'update_funding_pool': -funding,
            'update_journal': to_journal,
            'update_researcher_done': salary,
            'update_losses': losses}

def s_researcher_value(params, substep, state_history, previous_state, policy_input):
    research_funding = policy_input['update_researcher_funding']
    research_salary = policy_input['update_researcher_done']
    research_value = previous_state['researcher_value']

    if research_salary == 0:
        updated_researcher_value = research_funding + research_value
        return 'researcher_value', updated_researcher_value
    else:
        updated_researcher_value = research_salary + research_value
        return 'researcher_value', updated_researcher_value

def s_journal_value(params, substep, state_history, previous_state, policy_input):
    to_journal = policy_input['update_journal']
    journal_value = previous_state['journal_value']

    updated_journal_value = to_journal + journal_value

    return 'journal_value', updated_journal_value

def s_funding_pool(params, substep, state_history, previous_state, policy_input):
    funding_pool = previous_state['funding_pool']
    updated_funding_pool = funding_pool + policy_input['update_funding_pool']
    if updated_funding_pool < 0:
        updated_funding_pool = 0
    return 'funding_pool', updated_funding_pool

def s_losses(params, substep, state_history, previous_state, policy_input):
    losses = previous_state['losses']
    updated_losses = losses + policy_input['update_losses']
    return 'losses', updated_losses

st.subheader('Initial Value Allocation')
funding_pool = st.slider('Initial Funding Pool', min_value=1000, max_value=10000, value=1000, step=10)
researcher_value = st.slider('Initial Researcher Tokens', min_value=0, max_value=1000, value=0, step=1)
journal_value = st.slider('Initial Journal Tokens', min_value=0, max_value=1000, value=0, step=1)
st.subheader('Simulation Parameters')
st.write('Set the funding disbursed each round from the funding pool')
funding_round = st.slider('Funding Round', min_value=100, max_value=1000, value=100, step=1)
st.write('Set the relative value leakages in the model.')
alpha = st.slider('Management Cost Weight', min_value=0., max_value=1., value=0.1, step=0.0001)
epsilon = st.slider('Work Inefficiency Weight', min_value=0., max_value=1., value=0.1, step=0.0001)
st.write('Set the portion of grant funding to be used as researcher salary.')
beta = st.slider('Salary Weight', min_value=0., max_value=1., value=0.4, step=0.0001)
st.write('Set the cost of publishing to a journal and the cost of getting access to papers.')
cost_publishing = st.slider('Cost of Publishing', min_value=10., max_value=100., value=10., step=0.1)
cost_buying = st.slider('Cost of Buying', min_value=10., max_value=100., value=10., step=0.1)
st.write('Set the probability a researcher will buy access to a paper at each timestep.')
probability_buying = st.slider('Researcher Probability of Buying', min_value=0., max_value=1., value=0.1, step=0.0001)
st.write('Set the probability the grant funding agency will disburse funding each round.')
probability_funding = st.slider('Probability of Disbursing Funding', min_value=0., max_value=1., value=0.9, step=0.0001)
st.write('Set the number of timesteps in the simulation.')
timesteps = st.slider('Timesteps', min_value=10, max_value=1000, value=100, step=1)

initial_state = {
    'funding_pool': funding_pool,
    'researcher_value': researcher_value,
    'journal_value': journal_value,
    'losses': 0
}

system_params = {
    'funding_pool': [funding_pool],
    'funding_round': [funding_round],
    'alpha': [alpha],
    'beta': [beta],
    'epsilon': [epsilon],
    'cost_publishing': [cost_publishing],
    'cost_buying': [cost_buying],
    'probability_buying': [probability_buying],
    'probability_funding': [probability_funding]
}

def generate_sim_config(monte_carlo_runs=1,
                   timesteps=timesteps,
                   system_params=system_params):
    sim_config = config_sim({
        'N': monte_carlo_runs, # the number of times we'll run the simulation ("Monte Carlo runs")
        'T': range(timesteps), # the number of timesteps the simulation will run for
        'M': system_params # the parameters of the system
    })

    return sim_config

def configure_experiment(initial_state,
                      partial_state_update_blocks,
                      sim_config):
    experiment = Experiment()
    experiment.append_configs(
        initial_state=initial_state,
        partial_state_update_blocks=partial_state_update_blocks,
        sim_configs=sim_config
    )

    return experiment

partial_state_update_blocks = [
    {
        'policies': {
            'p_value_flow': p_value_flow
        },
        'variables': {
            'funding_pool': s_funding_pool,
            'researcher_value': s_researcher_value,
            'journal_value': s_journal_value,
            'losses': s_losses
        }
    }
]

def execute_simulation(experiment):
    exec_context = ExecutionContext()
    configs = experiment.configs
    simulation = Executor(exec_context=exec_context, configs=configs)
    raw_result, tensor_field, sessions = simulation.execute()

    return raw_result

if st.button('Run Simulation'):
    sim_config = generate_sim_config()
    experiment = configure_experiment(initial_state, partial_state_update_blocks, sim_config)
    raw_result = execute_simulation(experiment)
    df = pd.DataFrame(raw_result)
    fig1 = df.plot(kind='line', x='timestep', y=['funding_pool','researcher_value', 'journal_value'], width=1000)
    fig2 = df.plot(kind='line', x='timestep', y=['funding_pool', 'losses'], width=1000)
    st.subheader('Results')
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
