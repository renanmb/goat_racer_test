## Notes about the Project

Project created with the IsaacLab tool, descriptions below:

```bash
./isaaclab.sh --new
[INFO] Installing template dependencies...                                                                                                                                                

[INFO] Running template generator...

? Task type: External
? Project path: /home/goat/Documents/GitHub/boredengineer/
? Project name: leatherback

      RL environment features support according to Isaac Lab workflows      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Environment feature                             ┃ Direct ┃ Manager-based ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Single-agent                                    │  yes   │      yes      │
│ Multi-agent                                     │  yes   │      no       │
│ Fundamental/composite spaces (apart from 'Box') │  yes   │      no       │
└─────────────────────────────────────────────────┴────────┴───────────────┘
? Isaac Lab workflow: Direct | single-agent

                                Supported RL libraries                                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ RL/training feature          ┃ rl_games ┃ rsl_rl  ┃ skrl                  ┃ sb3     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ ML frameworks                │ PyTorch  │ PyTorch │ PyTorch, JAX          │ PyTorch │
│ Relative performance         │ ~1X      │ ~1X     │ ~1X                   │ ~0.03X  │
│ Algorithms                   │ PPO      │ PPO     │ AMP, IPPO, MAPPO, PPO │ PPO     │
│ Multi-agent support          │ no       │ no      │ yes                   │ no      │
│ Distributed training         │ yes      │ no      │ yes                   │ no      │
│ Vectorized training          │ yes      │ yes     │ yes                   │ no      │
│ Fundamental/composite spaces │ no       │ no      │ yes                   │ no      │
└──────────────────────────────┴──────────┴─────────┴───────────────────────┴─────────┘
? RL library: rsl_rl, skrl
? RL algorithms for skrl: PPO

Validating specification...
Generating external project...
  |-- Copying repo files...
  |-- Copying scripts...
  |-- Copying extension files...
  |-- Generating tasks...
  |    |-- Generating 'Template-Leatherback-Direct-v0' task...
  |-- Copying vscode files...
Setting up git repo in /home/goat/Documents/GitHub/boredengineer/leatherback path...
  |  Initialized empty Git repository in /home/goat/Documents/GitHub/boredengineer/leatherback/.git/

--------------------------------------------------------------------------------
Project 'leatherback' generated successfully in /home/goat/Documents/GitHub/boredengineer/leatherback path.
See /home/goat/Documents/GitHub/boredengineer/leatherback/README.md to get started!
--------------------------------------------------------------------------------
```