#include "money_state.h"

extern "C" void SetSuperCompanyMoney(SuperMoneyState* state, long long value)
{
    state->company_money = value;
}
