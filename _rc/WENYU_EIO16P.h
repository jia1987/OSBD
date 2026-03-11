typedef		VOID	( CALLBACK	* InterruptFun ) ( VOID );
typedef unsigned char UCHAR;
extern "C" int _declspec(dllexport) WY_Open();
//关闭卡
extern "C" int _declspec(dllexport) WY_Close();
extern "C" int _declspec(dllexport) WY_ResetInterrupt(int CardNo);
extern "C" int _declspec(dllexport) WY_GetInterruptData(int CardNo,unsigned char &RiseData,unsigned char &FallData);


extern "C" int _declspec(dllexport) WY_SetInterruptFun(int CardNo,InterruptFun 	iIntRoutine);


extern "C" int _declspec(dllexport) WY_SetInterruptPortEnable(int CardNo,UCHAR RiseEnable,UCHAR FallEnable);

extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort(int CardNo,int portbit );
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort0(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort1(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort2(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort3(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort4(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort5(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort6(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptRisePort7(int CardNo);

extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort(int CardNo,int portbit );
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort0(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort1(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort2(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort3(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort4(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort5(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort6(int CardNo);
extern "C" int _declspec(dllexport) WY_ClrInterruptFallPort7(int CardNo);

extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit(int CardNo,int portbit,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit0(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit1(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit2(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit3(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit4(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit5(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit6(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetRiseInterruptPortEnableBit7(int CardNo,int value);

extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit(int CardNo,int portbit,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit0(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit1(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit2(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit3(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit4(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit5(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit6(int CardNo,int value);
extern "C" int _declspec(dllexport)WY_SetFallInterruptPortEnableBit7(int CardNo,int value);



extern "C" int _declspec(dllexport) WY_SetInterruptEnable(int CardNo,int Enable);

//获取版本号
extern "C" int _declspec(dllexport) WY_GetCardVersion(int CardNo,long &VerNumber);




extern "C" int _declspec(dllexport) WY_GetInPutData(int CardNo,unsigned char &Data);


extern "C" int _declspec(dllexport)  WY_GetOutPutData(int CardNo,unsigned char &OutPutData);


extern "C" int _declspec(dllexport)  WY_SetOutPutData(int CardNo,unsigned char OutPutData);


extern "C" int _declspec(dllexport) WY_WriteOutPutBit0(int CardNo, int value) ;


extern "C" int _declspec(dllexport) WY_WriteOutPutBit1(int CardNo, int value) ;

extern "C" int _declspec(dllexport) WY_WriteOutPutBit2(int CardNo, int value); 


extern "C" int _declspec(dllexport) WY_WriteOutPutBit3(int CardNo, int value); 


extern "C" int _declspec(dllexport) WY_WriteOutPutBit4(int CardNo, int value); 


extern "C" int _declspec(dllexport) WY_WriteOutPutBit5(int CardNo, int value) ;


extern "C" int _declspec(dllexport) WY_WriteOutPutBit6(int CardNo, int value); 


extern "C" int _declspec(dllexport) WY_WriteOutPutBit7(int CardNo, int value); 


extern "C" int _declspec(dllexport) WY_WriteOutPutBit(int CardNo,int bit, int value); 

extern "C" int _declspec(dllexport) WY_ReadInPutbit0(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit1(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit2(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit3(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit4(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit5(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit6(int CardNo,int &value);
extern "C" int _declspec(dllexport) WY_ReadInPutbit7(int CardNo,int &value);

extern "C" int _declspec(dllexport) WY_ReadInPutbit(int CardNo,int portbit,int &value);


extern "C" int _declspec(dllexport) WY_ReadOutPutBit0(int CardNo,int &value);


extern "C" int _declspec(dllexport) WY_ReadOutPutBit1(int CardNo,int &value);

extern "C" int _declspec(dllexport) WY_ReadOutPutBit2(int CardNo,int &value);


extern "C" int _declspec(dllexport) WY_ReadOutPutBit3(int CardNo,int &value);


extern "C" int _declspec(dllexport) WY_ReadOutPutBit4(int CardNo,int &value);

extern "C" int _declspec(dllexport) WY_ReadOutPutBit5(int CardNo,int &value);


extern "C" int _declspec(dllexport) WY_ReadOutPutBit6(int CardNo,int &value);

extern "C" int _declspec(dllexport) WY_ReadOutPutBit7(int CardNo,int &value);

extern "C" int _declspec(dllexport) WY_ReadOutPutBit(int CardNo,int portbit,int &value);
