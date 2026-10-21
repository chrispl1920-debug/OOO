#include "money_state.h"

extern "C" void SetSuperGameMoney(SuperMoneyState* state, long long value)
{
    state->game_money = value;
}
