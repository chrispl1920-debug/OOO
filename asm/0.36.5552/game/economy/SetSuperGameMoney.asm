; Original instructions observed at RVA 0x1e33610 in the pinned executable.
; Function names are assigned through Unreal native registration and wrapper calls.
.code
PUBLIC SetSuperGameMoney
SetSuperGameMoney PROC
    mov QWORD PTR [rcx+2B8h], rdx
    ret
SetSuperGameMoney ENDP
END
