LOGICAL FUNCTION FALGRA (KNGRIB)
!****
!    Cette fonction renvoie une valeur vraie si la methode d'encodage passee en argument fait appel a grib_api
!**
!    Arguments : KNGRIB (Entree) ==> Methode d'encodage
!
!
INTEGER (KIND=JPLIKB) KNGRIB
INTEGER (KIND=JPLIKB) INGRIB_SP, INGRIB_GP
LOGICAL LLFALGRA_SP, LLFALGRA_GP

FALGRA = .FALSE.


IF (100 <= KNGRIB .AND. KNGRIB <= 240) THEN

  INGRIB_SP = FALGRA_SP (KNGRIB)
  INGRIB_GP = FALGRA_GP (KNGRIB)

  LLFALGRA_SP = &
   & (INGRIB_SP - 100 ==  1) .OR. &      ! GRIB2 complex packing (bug)
   & (INGRIB_SP - 100 ==  2) .OR. &      ! GRIB0 
   & (INGRIB_SP - 100 ==  3) .OR. &      ! GRIB2 complex packing
   & (INGRIB_SP - 100 ==  4)             ! GRIB2 ccsds packing 

  LLFALGRA_GP = &
   & ((INGRIB_GP-100) / 20 ==  1) .OR. & ! GRIB2 simple packing
   & ((INGRIB_GP-100) / 20 ==  2) .OR. & ! GRIB2 second order packing
   & ((INGRIB_GP-100) / 20 ==  3) .OR. & ! GRIB1 simple packing
   & ((INGRIB_GP-100) / 20 ==  4) .OR. & ! GRIB1 second order packing
   & ((INGRIB_GP-100) / 20 ==  5) .OR. & ! GRIB2 complex packing
   & ((INGRIB_GP-100) / 20 ==  6)        ! GRIB2 ccsds packing
   

  IF (LLFALGRA_GP .AND. LLFALGRA_SP) THEN
    FALGRA = .TRUE.
  ELSEIF (LLFALGRA_GP) THEN
    FALGRA = INGRIB_SP == 100
  ELSEIF (LLFALGRA_SP) THEN
    FALGRA = INGRIB_GP == 100
  ENDIF

ENDIF

END FUNCTION FALGRA

INTEGER (KIND=JPLIKB) FUNCTION FALGRA_SP (KNGRIB)
INTEGER (KIND=JPLIKB) KNGRIB
FALGRA_SP = 100+MODULO ((KNGRIB-100),20)
END FUNCTION FALGRA_SP

INTEGER (KIND=JPLIKB) FUNCTION FALGRA_GP (KNGRIB)
INTEGER (KIND=JPLIKB) KNGRIB
FALGRA_GP = 100+20*((KNGRIB-100)/20)
END FUNCTION FALGRA_GP

INTEGER (KIND=JPLIKB) FUNCTION FALGRA_ED (KNGRIB)
INTEGER (KIND=JPLIKB) KNGRIB

SELECT CASE (KNGRIB)
  CASE (160, 180)
    FALGRA_ED = 1
  CASE DEFAULT
    FALGRA_ED = 2
END SELECT 

END FUNCTION FALGRA_ED

