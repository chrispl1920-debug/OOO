#pragma once

// Partial memory views recovered from machine code, not the original class definitions.
// Padding names and function signatures are reconstruction choices.
struct RewardMoneyState {
    unsigned char unknown[0x48];
    int reward_money;
};

struct PersonalMoneyState {
    unsigned char unknown[0x7ac];
    int personal_money;
};

struct SuperMoneyState {
    unsigned char unknown[0x2b0];
    long long company_money;
    long long game_money;
};

static_assert(sizeof(int) == 4 && sizeof(long long) == 8);

extern "C" void SetRewardMoney(RewardMoneyState*, int);
extern "C" void SetPersonalMoney(PersonalMoneyState*, int);
extern "C" void SetSuperGameMoney(SuperMoneyState*, long long);
extern "C" void SetSuperCompanyMoney(SuperMoneyState*, long long);
