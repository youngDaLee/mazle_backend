CREATE DEFINER=`dylee`@`%` PROCEDURE `sp_drink_like_delete` (
     IN `i_customer_uuid`     VARCHAR(40)      -- 유저ID
    ,IN `i_drink_id`         INTEGER          -- 음료ID
    ,OUT `o_out_code`         SMALLINT
)

BEGIN
/* ----------------------------------------------------------------------------
sp_drink_like_set : 음료 좋아요 삭제
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


    START TRANSACTION;

    -- 1. 데이터 삭제
    DELETE FROM drink_like
    WHERE customer_uuid=i_customer_uuid
      AND drink_id=i_drink_id;

    COMMIT;

END