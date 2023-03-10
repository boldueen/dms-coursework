-- DROP ROLE IF EXISTS SHOP_USER;
-- DROP ROLE IF EXISTS SHOP_ADMIN;
 
-- CREATE ROLE SHOP_USER;
-- CREATE ROLE SHOP_ADMIN;

REVOKE ALL PRIVILEGES on SCHEMA public FROM SHOP_USER;
GRANT USAGE ON SCHEMA public to SHOP_USER;


GRANT USAGE ON SCHEMA public TO SHOP_USER;
GRANT USAGE ON SCHEMA public TO SHOP_ADMIN;

GRANT SELECT on users, 
                categories, 
                items, 
                offices, 
                orders, 
                orders_items 
            to SHOP_USER, SHOP_ADMIN;


GRANT USAGE, SELECT, UPDATE
    ON ALL SEQUENCES IN SCHEMA public
    TO SHOP_ADMIN;
	
GRANT SELECT, UPDATE, INSERT
    ON ALL TABLES IN SCHEMA public
    TO SHOP_ADMIN;	

DROP ROLE IF EXISTS alez_pro;
CREATE ROLE alez_pro;
GRANT SHOP_USER TO alez_pro;

DROP ROLE IF EXISTS real_admin;
CREATE ROLE real_admin;
GRANT SHOP_ADMIN TO real_admin;

DROP ROLE IF EXISTS bbolq;
CREATE ROLE bbolq;
GRANT SHOP_USER TO bbolq;

DROP ROLE IF EXISTS jojo;
CREATE ROLE jojo;
GRANT SHOP_USER TO jojo;