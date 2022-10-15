CREATE DEFINER=`dylee`@`%` PROCEDURE `sp_drink_like_select` (
     IN i_customer_uuid     VARCHAR(40)     -- 유저ID, NOT NULL
    ,IN i_drink_id         VARCHAR(40)     -- 음료ID
    ,OUT `o_out_code`       SMALLINT
)

BEGIN
/* ----------------------------------------------------------------------------
sp_drink_like_select : 음료 좋아요 조회
author : dylee
RELEASE : 0.0.1
LAST UPDATE : 2022-10-16
---------------------------------------------------------------------------- */ 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION, NOT FOUND, SQLWARNING
    BEGIN
        GET DIAGNOSTICS CONDITION 1 @v_sql_state = RETURNED_SQLSTATE
                , @v_error_no = MYSQL_ERRNO
                , @v_error_msg = MESSAGE_TEXT;
                SELECT @v_error_msg ; 
        ROLLBACK;
        SET o_out_code = -99;
    END;

    SET o_out_code = 0;

    IF (i_drink_id IS NOT NULL)
    THEN
        -- 1. 해당 drink에 대해 좋아요 여부
        SELECT drink_id
        FROM drink_like
        WHERE customer_uuid=i_customer_uuid
          AND drink_id=i_drink_id;

    ELSE
        -- 2. 유저 전제 음료 좋아요 여부
        SELECT drink_id
        FROM drink_like
        WHERE customer_uuid=i_customer_uuid;

    END IF;

END