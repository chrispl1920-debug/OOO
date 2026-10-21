#include "money_state.h"

extern "C" void SetPersonalMoney(PersonalMoneyState* state, int value)
{
    state->personal_money = value;
}
