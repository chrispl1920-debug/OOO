; Original instructions observed at RVA 0x1e33490 in the pinned executable.
; Function names are assigned through Unreal native registration and wrapper calls.
.code
PUBLIC SetRewardMoney
SetRewardMoney PROC
    mov DWORD PTR [rcx+48h], edx
    ret
SetRewardMoney ENDP
END
