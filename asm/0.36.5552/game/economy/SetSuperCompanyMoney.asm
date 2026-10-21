; Original instructions observed at RVA 0x1df6df0 in the pinned executable.
; Function names are assigned through Unreal native registration and wrapper calls.
.code
PUBLIC SetSuperCompanyMoney
SetSuperCompanyMoney PROC
    mov QWORD PTR [rcx+2B0h], rdx
    ret
SetSuperCompanyMoney ENDP
END
