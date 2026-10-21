; Original instructions observed at RVA 0x1e33030 in the pinned executable.
; Function names are assigned through Unreal native registration and wrapper calls.
.code
PUBLIC SetPersonalMoney
SetPersonalMoney PROC
    mov DWORD PTR [rcx+7ACh], edx
    ret
SetPersonalMoney ENDP
END
