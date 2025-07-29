/*      Compiler: ECL 24.5.10                                         */
/*      Date: 2025/6/30 10:51 (yyyy/mm/dd)                            */
/*      Machine: Darwin 23.6.0 arm64                                  */
/*      Source: /Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/TBAGG-.lsp */
#include <ecl/ecl-cmp.h>
#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/TBAGG-.eclh"
/*      function definition for TBAGG-;table;S;1                      */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2550_tbagg__table_s_1_(cl_object v1_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v2;
  v2 = (v1_)->vector.self.t[9];
  T0 = _ecl_car(v2);
  T1 = _ecl_cdr(v2);
  value0 = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  return value0;
 }
}
/*      function definition for TBAGG-;table;LS;2                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2551_tbagg__table_ls_2_(cl_object v1_l_, cl_object v2_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[13];
  T0 = _ecl_car(v3);
  T1 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(2, v1_l_, T1);
  return value0;
 }
}
/*      function definition for TBAGG-;insert!;R2S;3                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2552_tbagg__insert__r2s_3_(cl_object v1_p_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[15];
  T0 = _ecl_car(v4);
  T1 = ECL_CONS_CAR(v1_p_);
  T2 = ECL_CONS_CDR(v1_p_);
  T3 = _ecl_cdr(v4);
  (cl_env_copy->function=T0)->cfun.entry(4, v2_t_, T1, T2, T3);
 }
 value0 = v2_t_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for TBAGG-;indices;SL;4                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2553_tbagg__indices_sl_4_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[18];
  T0 = _ecl_car(v3);
  T1 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1);
  return value0;
 }
}
/*      function definition for TBAGG-;coerce;SOf;5                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2554_tbagg__coerce_sof_5_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  cl_object v4_k_;
  cl_object v5;
  v3 = ECL_NIL;
  v4_k_ = ECL_NIL;
  v5 = ECL_NIL;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[28];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v2_)->vector.self.t[22];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, VV[5], T3);
   }
   v5 = ECL_NIL;
   v4_k_ = ECL_NIL;
   {
    cl_object v7;
    v7 = (v2_)->vector.self.t[18];
    T3 = _ecl_car(v7);
    T4 = _ecl_cdr(v7);
    v3 = (cl_env_copy->function=T3)->cfun.entry(2, v1_t_, T4);
   }
L13:;
   if (ECL_ATOM(v3)) { goto L23; }
   v4_k_ = _ecl_car(v3);
   goto L21;
L23:;
   goto L14;
L21:;
   {
    cl_object v7;
    v7 = (v2_)->vector.self.t[26];
    T4 = _ecl_car(v7);
    {
     cl_object v8;
     v8 = (v2_)->vector.self.t[23];
     T6 = _ecl_car(v8);
     T7 = _ecl_cdr(v8);
     T5 = (cl_env_copy->function=T6)->cfun.entry(2, v4_k_, T7);
    }
    {
     cl_object v8;
     v8 = (v2_)->vector.self.t[25];
     T7 = _ecl_car(v8);
     {
      cl_object v9;
      v9 = (v2_)->vector.self.t[24];
      T9 = _ecl_car(v9);
      T10 = _ecl_cdr(v9);
      T8 = (cl_env_copy->function=T9)->cfun.entry(3, v1_t_, v4_k_, T10);
     }
     T9 = _ecl_cdr(v8);
     T6 = (cl_env_copy->function=T7)->cfun.entry(2, T8, T9);
    }
    T7 = _ecl_cdr(v7);
    T3 = (cl_env_copy->function=T4)->cfun.entry(3, T5, T6, T7);
   }
   v5 = CONS(T3,v5);
   goto L27;
L27:;
   v3 = _ecl_cdr(v3);
   goto L13;
L14:;
   T2 = cl_nreverse(v5);
   goto L12;
L12:;
   T3 = _ecl_cdr(v6);
   value0 = (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
   return value0;
  }
 }
}
/*      function definition for TBAGG-;elt;SKeyEntry;6                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2555_tbagg__elt_skeyentry_6_(cl_object v1_t_, cl_object v2_k_, cl_object v3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_r_;
  v4_r_ = ECL_NIL;
  {
   cl_object v5;
   v5 = (v3_)->vector.self.t[31];
   T0 = _ecl_car(v5);
   T1 = _ecl_cdr(v5);
   v4_r_ = (cl_env_copy->function=T0)->cfun.entry(3, v2_k_, v1_t_, T1);
  }
  T0 = ECL_CONS_CAR(v4_r_);
  if (!((ecl_fixnum(T0))==(0))) { goto L7; }
  value0 = ECL_CONS_CDR(v4_r_);
  cl_env_copy->nvalues = 1;
  return value0;
L7:;
  value0 = ecl_function_dispatch(cl_env_copy,VV[39])(1, VV[7]) /*  error */;
  return value0;
 }
}
/*      function definition for TBAGG-;elt;SKey2Entry;7               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2556_tbagg__elt_skey2entry_7_(cl_object v1_t_, cl_object v2_k_, cl_object v3_e_, cl_object v4_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_r_;
  v5_r_ = ECL_NIL;
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[31];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v5_r_ = (cl_env_copy->function=T0)->cfun.entry(3, v2_k_, v1_t_, T1);
  }
  T0 = ECL_CONS_CAR(v5_r_);
  if (!((ecl_fixnum(T0))==(0))) { goto L7; }
  value0 = ECL_CONS_CDR(v5_r_);
  cl_env_copy->nvalues = 1;
  return value0;
L7:;
  value0 = v3_e_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;map!;M2S;8                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2557_tbagg__map__m2s_8_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5_k_;
  v4 = ECL_NIL;
  v5_k_ = ECL_NIL;
  v5_k_ = ECL_NIL;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v4 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L4:;
  if (ECL_ATOM(v4)) { goto L14; }
  v5_k_ = _ecl_car(v4);
  goto L12;
L14:;
  goto L5;
L12:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[15];
   T0 = _ecl_car(v6);
   T2 = _ecl_car(v1_f_);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[24];
    T4 = _ecl_car(v7);
    T5 = _ecl_cdr(v7);
    T3 = (cl_env_copy->function=T4)->cfun.entry(3, v2_t_, v5_k_, T5);
   }
   T4 = _ecl_cdr(v1_f_);
   T1 = (cl_env_copy->function=T2)->cfun.entry(2, T3, T4);
   T2 = _ecl_cdr(v6);
   (cl_env_copy->function=T0)->cfun.entry(4, v2_t_, v5_k_, T1, T2);
   goto L18;
  }
L18:;
  v4 = _ecl_cdr(v4);
  goto L4;
L5:;
  goto L3;
L3:;
  value0 = v2_t_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;map;M3S;9                      */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2558_tbagg__map_m3s_9_(cl_object v1_f_, cl_object v2_s_, cl_object v3_t_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  cl_object v6_k_;
  cl_object v7_z_;
  v5 = ECL_NIL;
  v6_k_ = ECL_NIL;
  v7_z_ = ECL_NIL;
  {
   cl_object v8;
   v8 = (v4_)->vector.self.t[36];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   v7_z_ = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  }
  v6_k_ = ECL_NIL;
  {
   cl_object v8;
   v8 = (v4_)->vector.self.t[18];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   v5 = (cl_env_copy->function=T0)->cfun.entry(2, v2_s_, T1);
  }
L9:;
  if (ECL_ATOM(v5)) { goto L19; }
  v6_k_ = _ecl_car(v5);
  goto L17;
L19:;
  goto L10;
L17:;
  {
   cl_object v8;
   v8 = (v4_)->vector.self.t[38];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v6_k_, v3_t_, T1))) { goto L23; }
  }
  {
   cl_object v8;
   v8 = (v4_)->vector.self.t[15];
   T0 = _ecl_car(v8);
   T2 = _ecl_car(v1_f_);
   {
    cl_object v9;
    v9 = (v4_)->vector.self.t[24];
    T4 = _ecl_car(v9);
    T5 = _ecl_cdr(v9);
    T3 = (cl_env_copy->function=T4)->cfun.entry(3, v2_s_, v6_k_, T5);
   }
   {
    cl_object v9;
    v9 = (v4_)->vector.self.t[24];
    T5 = _ecl_car(v9);
    T6 = _ecl_cdr(v9);
    T4 = (cl_env_copy->function=T5)->cfun.entry(3, v3_t_, v6_k_, T6);
   }
   T5 = _ecl_cdr(v1_f_);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, T4, T5);
   T2 = _ecl_cdr(v8);
   (cl_env_copy->function=T0)->cfun.entry(4, v7_z_, v6_k_, T1, T2);
   goto L23;
  }
L23:;
  v5 = _ecl_cdr(v5);
  goto L9;
L10:;
  goto L8;
L8:;
  value0 = v7_z_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;parts;SL;10                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2559_tbagg__parts_sl_10_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  cl_object v4_k_;
  cl_object v5;
  v3 = ECL_NIL;
  v4_k_ = ECL_NIL;
  v5 = ECL_NIL;
  v5 = ECL_NIL;
  v4_k_ = ECL_NIL;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[18];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v3 = (cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1);
  }
L7:;
  if (ECL_ATOM(v3)) { goto L17; }
  v4_k_ = _ecl_car(v3);
  goto L15;
L17:;
  goto L8;
L15:;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[24];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v1_t_, v4_k_, T2);
  }
  T1 = CONS(v4_k_,T0);
  v5 = CONS(T1,v5);
  goto L21;
L21:;
  v3 = _ecl_cdr(v3);
  goto L7;
L8:;
  value0 = cl_nreverse(v5);
  return value0;
 }
}
/*      function definition for TBAGG-;parts;SL;11                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2560_tbagg__parts_sl_11_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  cl_object v4_k_;
  cl_object v5;
  v3 = ECL_NIL;
  v4_k_ = ECL_NIL;
  v5 = ECL_NIL;
  v5 = ECL_NIL;
  v4_k_ = ECL_NIL;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[18];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v3 = (cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1);
  }
L7:;
  if (ECL_ATOM(v3)) { goto L17; }
  v4_k_ = _ecl_car(v3);
  goto L15;
L17:;
  goto L8;
L15:;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[24];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v1_t_, v4_k_, T2);
  }
  v5 = CONS(T0,v5);
  goto L21;
L21:;
  v3 = _ecl_cdr(v3);
  goto L7;
L8:;
  value0 = cl_nreverse(v5);
  return value0;
 }
}
/*      function definition for TBAGG-;entries;SL;12                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2561_tbagg__entries_sl_12_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[44];
  T0 = _ecl_car(v3);
  T1 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1);
  return value0;
 }
}
/*      function definition for TBAGG-;=;2SB;13                       */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2562_tbagg____2sb_13_(cl_object v1_s_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5;
  cl_object v6_e_;
  cl_object v7;
  cl_object v8_k_;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_e_ = ECL_NIL;
  v7 = ECL_NIL;
  v8_k_ = ECL_NIL;
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[46];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, v1_s_, v2_t_, T1))) { goto L8; }
  }
  value0 = ECL_T;
  cl_env_copy->nvalues = 1;
  return value0;
L8:;
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[50];
   T0 = _ecl_car(v9);
   {
    cl_object v10;
    v10 = (v3_)->vector.self.t[48];
    T2 = _ecl_car(v10);
    T3 = _ecl_cdr(v10);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v1_s_, T3);
   }
   {
    cl_object v10;
    v10 = (v3_)->vector.self.t[48];
    T3 = _ecl_car(v10);
    T4 = _ecl_cdr(v10);
    T2 = (cl_env_copy->function=T3)->cfun.entry(2, v2_t_, T4);
   }
   T3 = _ecl_cdr(v9);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3))) { goto L12; }
  }
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L12:;
  v8_k_ = ECL_NIL;
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   v7 = (cl_env_copy->function=T0)->cfun.entry(2, v1_s_, T1);
  }
L25:;
  if (ECL_ATOM(v7)) { goto L35; }
  v8_k_ = _ecl_car(v7);
  goto L33;
L35:;
  goto L26;
L33:;
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[31];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   v6_e_ = (cl_env_copy->function=T0)->cfun.entry(3, v8_k_, v2_t_, T1);
  }
  T0 = ECL_CONS_CAR(v6_e_);
  if ((ecl_fixnum(T0))==(1)) { goto L46; }
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[51];
   T0 = _ecl_car(v9);
   T1 = ECL_CONS_CDR(v6_e_);
   {
    cl_object v10;
    v10 = (v3_)->vector.self.t[24];
    T3 = _ecl_car(v10);
    T4 = _ecl_cdr(v10);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_s_, v8_k_, T4);
   }
   T3 = _ecl_cdr(v9);
   if (Null((cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3))) { goto L39; }
   goto L45;
  }
L46:;
L45:;
  v5 = ECL_NIL;
  goto L6;
  goto L23;
L39:;
  v7 = _ecl_cdr(v7);
  goto L25;
L26:;
  goto L22;
L23:;
  goto L22;
L22:;
  value0 = ECL_T;
  cl_env_copy->nvalues = 1;
  return value0;
L6:;
  value0 = v5;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;map;M2S;14                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2563_tbagg__map_m2s_14_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_ke_;
  cl_object v5;
  cl_object v6_k_;
  cl_object v7_z_;
  v4_ke_ = ECL_NIL;
  v5 = ECL_NIL;
  v6_k_ = ECL_NIL;
  v7_z_ = ECL_NIL;
  {
   cl_object v8;
   v8 = (v3_)->vector.self.t[36];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   v7_z_ = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  }
  v6_k_ = ECL_NIL;
  {
   cl_object v8;
   v8 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v8);
   T1 = _ecl_cdr(v8);
   v5 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L10:;
  if (ECL_ATOM(v5)) { goto L20; }
  v6_k_ = _ecl_car(v5);
  goto L18;
L20:;
  goto L11;
L18:;
  T0 = _ecl_car(v1_f_);
  {
   cl_object v8;
   v8 = (v3_)->vector.self.t[24];
   T2 = _ecl_car(v8);
   T3 = _ecl_cdr(v8);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v2_t_, v6_k_, T3);
  }
  T2 = CONS(v6_k_,T1);
  T3 = _ecl_cdr(v1_f_);
  v4_ke_ = (cl_env_copy->function=T0)->cfun.entry(2, T2, T3);
  {
   cl_object v8;
   v8 = (v3_)->vector.self.t[15];
   T0 = _ecl_car(v8);
   T1 = ECL_CONS_CAR(v4_ke_);
   T2 = ECL_CONS_CDR(v4_ke_);
   T3 = _ecl_cdr(v8);
   (cl_env_copy->function=T0)->cfun.entry(4, v7_z_, T1, T2, T3);
   goto L24;
  }
L24:;
  v5 = _ecl_cdr(v5);
  goto L10;
L11:;
  goto L9;
L9:;
  value0 = v7_z_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;map!;M2S;15                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2564_tbagg__map__m2s_15_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5_ke_;
  cl_object v6_lke_;
  cl_object v7;
  cl_object v8;
  cl_object v9_k_;
  v4 = ECL_NIL;
  v5_ke_ = ECL_NIL;
  v6_lke_ = ECL_NIL;
  v7 = ECL_NIL;
  v8 = ECL_NIL;
  v9_k_ = ECL_NIL;
  v6_lke_ = ECL_NIL;
  v9_k_ = ECL_NIL;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v10);
   T1 = _ecl_cdr(v10);
   v8 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L10:;
  if (ECL_ATOM(v8)) { goto L20; }
  v9_k_ = _ecl_car(v8);
  goto L18;
L20:;
  goto L11;
L18:;
  T1 = _ecl_car(v1_f_);
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[55];
   T2 = _ecl_car(v10);
   T3 = _ecl_cdr(v10);
   v7 = (cl_env_copy->function=T2)->cfun.entry(3, v9_k_, v2_t_, T3);
  }
  {
   cl_object v10;
   v10 = ECL_CONS_CDR(v7);
   T3 = ECL_CONS_CAR(v7);
   {
    bool v11;
    v11 = (ecl_fixnum(T3))==(0);
    if (!(ecl_make_bool(v11)==ECL_NIL)) { goto L35; }
   }
   T3 = (v3_)->vector.self.t[8];
   T4 = (v3_)->vector.self.t[8];
   T5 = ecl_function_dispatch(cl_env_copy,VV[49])(2, T4, VV[17]) /*  Union */;
   T6 = ecl_function_dispatch(cl_env_copy,VV[50])(3, v7, T3, T5) /*  check_union_failure_msg */;
   ecl_function_dispatch(cl_env_copy,VV[39])(1, T6) /*  error         */;
L35:;
   T2 = v10;
  }
  T3 = CONS(v9_k_,T2);
  T4 = _ecl_cdr(v1_f_);
  T0 = (cl_env_copy->function=T1)->cfun.entry(2, T3, T4);
  v6_lke_ = CONS(T0,v6_lke_);
  goto L24;
L24:;
  v8 = _ecl_cdr(v8);
  goto L10;
L11:;
  goto L9;
L9:;
  v5_ke_ = ECL_NIL;
  v4 = v6_lke_;
L42:;
  if (ECL_ATOM(v4)) { goto L50; }
  v5_ke_ = _ecl_car(v4);
  goto L48;
L50:;
  goto L43;
L48:;
  {
   cl_object v10;
   v10 = (v3_)->vector.self.t[15];
   T0 = _ecl_car(v10);
   T1 = ECL_CONS_CAR(v5_ke_);
   T2 = ECL_CONS_CDR(v5_ke_);
   T3 = _ecl_cdr(v10);
   (cl_env_copy->function=T0)->cfun.entry(4, v2_t_, T1, T2, T3);
   goto L54;
  }
L54:;
  v4 = _ecl_cdr(v4);
  goto L42;
L43:;
  goto L41;
L41:;
  value0 = v2_t_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;inspect;SR;16                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2565_tbagg__inspect_sr_16_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_ks_;
  v3_ks_ = ECL_NIL;
  {
   cl_object v4;
   v4 = (v2_)->vector.self.t[18];
   T0 = _ecl_car(v4);
   T1 = _ecl_cdr(v4);
   v3_ks_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1);
  }
  if (!(v3_ks_==ECL_NIL)) { goto L7; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[39])(1, VV[19]) /*  error */;
  return value0;
L7:;
  if (Null(v3_ks_)) { goto L10; }
  T0 = _ecl_car(v3_ks_);
  goto L9;
L10:;
  T0 = ecl_function_dispatch(cl_env_copy,VV[52])(0) /*  FIRST_ERROR   */;
L9:;
  {
   cl_object v4;
   v4 = (v2_)->vector.self.t[24];
   T2 = _ecl_car(v4);
   if (Null(v3_ks_)) { goto L16; }
   T3 = _ecl_car(v3_ks_);
   goto L15;
L16:;
   T3 = ecl_function_dispatch(cl_env_copy,VV[52])(0) /*  FIRST_ERROR  */;
L15:;
   T4 = _ecl_cdr(v4);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_t_, T3, T4);
  }
  value0 = CONS(T0,T1);
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;find;MSU;17                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2566_tbagg__find_msu_17_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5;
  cl_object v6_ke_;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_ke_ = ECL_NIL;
  v6_ke_ = ECL_NIL;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[58];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v5 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L7:;
  if (ECL_ATOM(v5)) { goto L17; }
  v6_ke_ = _ecl_car(v5);
  goto L15;
L17:;
  goto L8;
L15:;
  T0 = _ecl_car(v1_f_);
  T1 = _ecl_cdr(v1_f_);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v6_ke_, T1))) { goto L21; }
  v4 = CONS(ecl_make_fixnum(0),v6_ke_);
  goto L4;
L21:;
  v5 = _ecl_cdr(v5);
  goto L7;
L8:;
  goto L6;
L6:;
  value0 = CONS(ecl_make_fixnum(1),VV[17]);
  cl_env_copy->nvalues = 1;
  return value0;
L4:;
  value0 = v4;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;index?;KeySB;18                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2567_tbagg__index__keysb_18_(cl_object v1_k_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[31];
  T1 = _ecl_car(v4);
  T2 = _ecl_cdr(v4);
  T0 = (cl_env_copy->function=T1)->cfun.entry(3, v1_k_, v2_t_, T2);
 }
 T1 = ECL_CONS_CAR(T0);
 value0 = ecl_make_bool((ecl_fixnum(T1))==(0));
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for TBAGG-;remove!;R2S;19                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2568_tbagg__remove__r2s_19_(cl_object v1_x_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[63];
  T0 = _ecl_car(v4);
  T1 = _ecl_cdr(v4);
  if (Null((cl_env_copy->function=T0)->cfun.entry(3, v1_x_, v2_t_, T1))) { goto L1; }
 }
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[55];
  T0 = _ecl_car(v4);
  T1 = ECL_CONS_CAR(v1_x_);
  T2 = _ecl_cdr(v4);
  (cl_env_copy->function=T0)->cfun.entry(3, T1, v2_t_, T2);
 }
L1:;
 value0 = v2_t_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for TBAGG-;extract!;SR;20                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2569_tbagg__extract__sr_20_(cl_object v1_t_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_k_;
  v3_k_ = ECL_NIL;
  {
   cl_object v4;
   v4 = (v2_)->vector.self.t[65];
   T0 = _ecl_car(v4);
   T1 = _ecl_cdr(v4);
   v3_k_ = (cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1);
  }
  {
   cl_object v4;
   v4 = (v2_)->vector.self.t[55];
   T0 = _ecl_car(v4);
   T1 = ECL_CONS_CAR(v3_k_);
   T2 = _ecl_cdr(v4);
   (cl_env_copy->function=T0)->cfun.entry(3, T1, v1_t_, T2);
  }
  value0 = v3_k_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;any?;MSB;21                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2570_tbagg__any__msb_21_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5;
  cl_object v6_k_;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_k_ = ECL_NIL;
  v6_k_ = ECL_NIL;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v5 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L7:;
  if (ECL_ATOM(v5)) { goto L17; }
  v6_k_ = _ecl_car(v5);
  goto L15;
L17:;
  goto L8;
L15:;
  T0 = _ecl_car(v1_f_);
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[24];
   T2 = _ecl_car(v7);
   T3 = _ecl_cdr(v7);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v2_t_, v6_k_, T3);
  }
  T2 = _ecl_cdr(v1_f_);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, T1, T2))) { goto L21; }
  v4 = ECL_T;
  goto L4;
L21:;
  v5 = _ecl_cdr(v5);
  goto L7;
L8:;
  goto L6;
L6:;
  value0 = ECL_NIL;
  cl_env_copy->nvalues = 1;
  return value0;
L4:;
  value0 = v4;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;every?;MSB;22                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2571_tbagg__every__msb_22_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5;
  cl_object v6_k_;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_k_ = ECL_NIL;
  v6_k_ = ECL_NIL;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v5 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L7:;
  if (ECL_ATOM(v5)) { goto L17; }
  v6_k_ = _ecl_car(v5);
  goto L15;
L17:;
  goto L8;
L15:;
  T1 = _ecl_car(v1_f_);
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[24];
   T3 = _ecl_car(v7);
   T4 = _ecl_cdr(v7);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, v2_t_, v6_k_, T4);
  }
  T3 = _ecl_cdr(v1_f_);
  T0 = (cl_env_copy->function=T1)->cfun.entry(2, T2, T3);
  if (!(T0==ECL_NIL)) { goto L21; }
  v4 = ECL_NIL;
  goto L4;
L21:;
  v5 = _ecl_cdr(v5);
  goto L7;
L8:;
  goto L6;
L6:;
  value0 = ECL_T;
  cl_env_copy->nvalues = 1;
  return value0;
L4:;
  value0 = v4;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TBAGG-;count;MSNni;23                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2572_tbagg__count_msnni_23_(cl_object v1_f_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_tally_;
  cl_object v5;
  cl_object v6_k_;
  v4_tally_ = ecl_make_fixnum(0);
  v5 = ECL_NIL;
  v6_k_ = ECL_NIL;
  v4_tally_ = ecl_make_fixnum(0);
  v6_k_ = ECL_NIL;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[18];
   T0 = _ecl_car(v7);
   T1 = _ecl_cdr(v7);
   v5 = (cl_env_copy->function=T0)->cfun.entry(2, v2_t_, T1);
  }
L7:;
  if (ECL_ATOM(v5)) { goto L17; }
  v6_k_ = _ecl_car(v5);
  goto L15;
L17:;
  goto L8;
L15:;
  T0 = _ecl_car(v1_f_);
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[24];
   T2 = _ecl_car(v7);
   T3 = _ecl_cdr(v7);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v2_t_, v6_k_, T3);
  }
  T2 = _ecl_cdr(v1_f_);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, T1, T2))) { goto L21; }
  v4_tally_ = ecl_plus(v4_tally_,ecl_make_fixnum(1));
  goto L21;
L21:;
  v5 = _ecl_cdr(v5);
  goto L7;
L8:;
  goto L6;
L6:;
  value0 = v4_tally_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for TableAggregate&                       */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2573_tableaggregate__(cl_object v1__1_, cl_object v2__2_, cl_object v3__3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_pv__;
  cl_object v5_;
  cl_object v6_dv__;
  cl_object v7dv_3;
  cl_object v8dv_2;
  cl_object v9dv_1;
  v4_pv__ = ECL_NIL;
  v5_ = ECL_NIL;
  v6_dv__ = ECL_NIL;
  v7dv_3 = ECL_NIL;
  v8dv_2 = ECL_NIL;
  v9dv_1 = ECL_NIL;
  v9dv_1 = ecl_function_dispatch(cl_env_copy,VV[61])(1, v1__1_) /*  devaluate */;
  v8dv_2 = ecl_function_dispatch(cl_env_copy,VV[61])(1, v2__2_) /*  devaluate */;
  v7dv_3 = ecl_function_dispatch(cl_env_copy,VV[61])(1, v3__3_) /*  devaluate */;
  v6_dv__ = cl_list(4, VV[27], v9dv_1, v8dv_2, v7dv_3);
  v5_ = ecl_function_dispatch(cl_env_copy,VV[62])(1, ecl_make_fixnum(71)) /*  GETREFV */;
  (v5_)->vector.self.t[0]= v6_dv__;
  v4_pv__ = ecl_function_dispatch(cl_env_copy,VV[63])(3, ecl_make_fixnum(0), ecl_make_fixnum(0), ECL_NIL) /*  buildPredVector */;
  (v5_)->vector.self.t[3]= v4_pv__;
  ecl_function_dispatch(cl_env_copy,VV[64])(1, v5_) /*  stuffDomainSlots */;
  (v5_)->vector.self.t[6]= v1__1_;
  (v5_)->vector.self.t[7]= v2__2_;
  (v5_)->vector.self.t[8]= v3__3_;
  v4_pv__ = (v5_)->vector.self.t[3];
  if (Null(ecl_function_dispatch(cl_env_copy,VV[65])(2, v2__2_, VV[28]) /*  HasCategory */)) { goto L26; }
  if (Null(ecl_function_dispatch(cl_env_copy,VV[65])(2, v3__3_, VV[28]) /*  HasCategory */)) { goto L26; }
  T0 = (VV[4]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[29]= T1;
L26:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[65])(2, v1__1_, VV[29]) /*  HasCategory */)) { goto L30; }
  T0 = (VV[11]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[41]= T1;
  T0 = (VV[12]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[43]= T1;
  T0 = (VV[13]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[45]= T1;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[65])(2, v3__3_, VV[30]) /*  HasCategory */)) { goto L38; }
  T0 = (VV[14]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[52]= T1;
L38:;
  T0 = (VV[15]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[54]= T1;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[65])(2, v3__3_, VV[30]) /*  HasCategory */)) { goto L43; }
  T0 = (VV[16]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[56]= T1;
L43:;
  T0 = (VV[18]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[57]= T1;
  T0 = (VV[20]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[61]= T1;
  T0 = (VV[21]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[62]= T1;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[65])(2, v3__3_, VV[30]) /*  HasCategory */)) { goto L52; }
  T0 = (VV[22]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[64]= T1;
L52:;
  T0 = (VV[23]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[66]= T1;
  T0 = (VV[24]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[68]= T1;
  T0 = (VV[25]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[69]= T1;
  T0 = (VV[26]->symbol.gfdef);
  T1 = CONS(T0,v5_);
  (v5_)->vector.self.t[70]= T1;
L30:;
  value0 = v5_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}

#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/TBAGG-.data"
#ifdef __cplusplus
extern "C"
#endif
ECL_DLLEXPORT void init_fas_CODE(cl_object flag)
{
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
 cl_object *VVtemp;
 if (flag != OBJNULL){
 Cblock = flag;
 #ifndef ECL_DYNAMIC_VV
 flag->cblock.data = VV;
 #endif
 flag->cblock.data_size = VM;
 flag->cblock.temp_data_size = VMtemp;
 flag->cblock.data_text = compiler_data_text;
 flag->cblock.cfuns_size = compiler_cfuns_size;
 flag->cblock.cfuns = compiler_cfuns;
 flag->cblock.source = ecl_make_constant_base_string("/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/TBAGG-.lsp",-1);
 return;}
 #ifdef ECL_DYNAMIC_VV
 VV = Cblock->cblock.data;
 #endif
 Cblock->cblock.data_text = (const cl_object *)"@EcLtAg:init_fas_CODE@";
 VVtemp = Cblock->cblock.temp_data;
 ECL_DEFINE_SETF_FUNCTIONS
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[0], ECL_SYM("LOCATION",1862), VVtemp[0], VVtemp[1]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[0], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[2]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[33]);                          /*  TBAGG-;table;S;1 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[1], ECL_SYM("LOCATION",1862), VVtemp[3], VVtemp[4]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[1], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[5]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[34]);                          /*  TBAGG-;table;LS;2 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[2], ECL_SYM("LOCATION",1862), VVtemp[6], VVtemp[7]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[2], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[8]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[35]);                          /*  TBAGG-;insert!;R2S;3 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[3], ECL_SYM("LOCATION",1862), VVtemp[9], VVtemp[10]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[3], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[36]);                          /*  TBAGG-;indices;SL;4 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[4], ECL_SYM("LOCATION",1862), VVtemp[12], VVtemp[13]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[4], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[37]);                          /*  TBAGG-;coerce;SOf;5 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[6], ECL_SYM("LOCATION",1862), VVtemp[14], VVtemp[15]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[6], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[16]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[38]);                          /*  TBAGG-;elt;SKeyEntry;6 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[8], ECL_SYM("LOCATION",1862), VVtemp[17], VVtemp[18]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[8], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[19]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[40]);                          /*  TBAGG-;elt;SKey2Entry;7 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[9], ECL_SYM("LOCATION",1862), VVtemp[20], VVtemp[21]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[9], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[41]);                          /*  TBAGG-;map!;M2S;8 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[10], ECL_SYM("LOCATION",1862), VVtemp[23], VVtemp[24]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[10], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[25]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[42]);                          /*  TBAGG-;map;M3S;9 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[11], ECL_SYM("LOCATION",1862), VVtemp[26], VVtemp[27]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[11], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[43]);                          /*  TBAGG-;parts;SL;10 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[12], ECL_SYM("LOCATION",1862), VVtemp[28], VVtemp[29]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[12], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[44]);                          /*  TBAGG-;parts;SL;11 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[13], ECL_SYM("LOCATION",1862), VVtemp[30], VVtemp[31]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[13], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[45]);                          /*  TBAGG-;entries;SL;12 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[14], ECL_SYM("LOCATION",1862), VVtemp[32], VVtemp[33]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[14], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[34]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[46]);                          /*  TBAGG-;=;2SB;13 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[15], ECL_SYM("LOCATION",1862), VVtemp[35], VVtemp[36]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[15], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[47]);                          /*  TBAGG-;map;M2S;14 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[16], ECL_SYM("LOCATION",1862), VVtemp[37], VVtemp[38]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[16], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[48]);                          /*  TBAGG-;map!;M2S;15 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[18], ECL_SYM("LOCATION",1862), VVtemp[39], VVtemp[40]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[18], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[51]);                          /*  TBAGG-;inspect;SR;16 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[20], ECL_SYM("LOCATION",1862), VVtemp[41], VVtemp[42]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[20], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[53]);                          /*  TBAGG-;find;MSU;17 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[21], ECL_SYM("LOCATION",1862), VVtemp[43], VVtemp[44]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[21], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[45]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[54]);                          /*  TBAGG-;index?;KeySB;18 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[22], ECL_SYM("LOCATION",1862), VVtemp[46], VVtemp[47]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[22], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[48]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[55]);                          /*  TBAGG-;remove!;R2S;19 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[23], ECL_SYM("LOCATION",1862), VVtemp[49], VVtemp[50]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[23], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[11]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[56]);                          /*  TBAGG-;extract!;SR;20 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[24], ECL_SYM("LOCATION",1862), VVtemp[51], VVtemp[52]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[24], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[57]);                          /*  TBAGG-;any?;MSB;21 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[25], ECL_SYM("LOCATION",1862), VVtemp[53], VVtemp[54]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[25], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[58]);                          /*  TBAGG-;every?;MSB;22 */
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[26], ECL_SYM("LOCATION",1862), VVtemp[55], VVtemp[56]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[26], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[22]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[59]);                          /*  TBAGG-;count;MSNni;23 */
  (cl_env_copy->function=(ECL_SYM("MAPC",545)->symbol.gfdef))->cfun.entry(2, ECL_SYM("PROCLAIM",668), VVtemp[57]) /*  MAPC */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[27], ECL_SYM("LOCATION",1862), VVtemp[58], VVtemp[59]) /*  ANNOTATE */;
  ecl_function_dispatch(cl_env_copy,ECL_SYM("ANNOTATE",1856))(4, VV[27], ECL_SYM("LAMBDA-LIST",1000), ECL_NIL, VVtemp[60]) /*  ANNOTATE */;
  ecl_cmp_defun(VV[60]);                          /*  TableAggregate& */
 {
  cl_object T0, T1, T2, T3;
  cl_object volatile env0 = ECL_NIL;
  T0 = ecl_function_dispatch(cl_env_copy,VV[66])(2, ecl_make_fixnum(1), VVtemp[63]) /*  makeByteWordVec2 */;
  T1 = ecl_function_dispatch(cl_env_copy,VV[66])(2, ecl_make_fixnum(70), VVtemp[66]) /*  makeByteWordVec2 */;
  T2 = cl_listX(4, T0, VVtemp[64], VVtemp[65], T1);
  T3 = cl_list(5, VVtemp[61], VVtemp[62], ECL_NIL, T2, VV[32]);
  ecl_function_dispatch(cl_env_copy,VV[67])(3, VV[27], VV[31], T3) /*  MAKEPROP */;
 }
}
