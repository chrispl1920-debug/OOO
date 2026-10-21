#include "../src/game/economy/money_state.h"
#include <cassert>
#include <climits>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <initializer_list>

static_assert(offsetof(RewardMoneyState, reward_money) == 0x48);
static_assert(offsetof(PersonalMoneyState, personal_money) == 0x7ac);
static_assert(offsetof(SuperMoneyState, company_money) == 0x2b0);
static_assert(offsetof(SuperMoneyState, game_money) == 0x2b8);

template<class State, class Value>
void check(void (*setter)(State*, Value), std::size_t offset, Value value)
{
    State actual;
    unsigned char expected[sizeof(State)];
    std::memset(&actual, 0xa5, sizeof(actual));
    std::memset(expected, 0xa5, sizeof(expected));
    std::memcpy(expected + offset, &value, sizeof(value));
    setter(&actual, value);
    // Check the whole partial object, so accidental changes to adjacent fields fail.
    assert(std::memcmp(&actual, expected, sizeof(actual)) == 0);
}

int main()
{
    for (int value : {INT_MIN, -1, 0, 1, INT_MAX}) {
        check(SetRewardMoney, 0x48, value);
        check(SetPersonalMoney, 0x7ac, value);
    }
    for (long long value : {LLONG_MIN, -1LL, 0LL, 1LL, LLONG_MAX}) {
        check(SetSuperCompanyMoney, 0x2b0, value);
        check(SetSuperGameMoney, 0x2b8, value);
    }
    std::puts("20 setter boundary/preservation cases passed");
}
