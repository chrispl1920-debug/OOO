#include "money_state.h"

extern "C" void SetRewardMoney(RewardMoneyState* state, int value)
{
    state->reward_money = value;
}
