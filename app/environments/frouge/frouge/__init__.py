from gymnasium.envs.registration import register

register(
    id='FlammeRouge-v0',
    entry_point='frouge.envs:FlammeRougeEnv',
)

# optimal training :
#docker-compose exec app python3 train.py -r -e frouge -t 250 -os 60 -ob 256 -dev cuda

