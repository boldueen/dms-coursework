-- extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;





/* Drop Tables */

DROP TABLE IF EXISTS buy_offers CASCADE;
DROP TABLE IF EXISTS orders_items CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS offices CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS users CASCADE;




/* Create Tables */

CREATE TABLE buy_offers
(
	supplier_id int NOT NULL UNIQUE,
	item_id int NOT NULL UNIQUE,
	item_name varchar(50) UNIQUE,
	offer_id serial NOT NULL UNIQUE,
	quantity int DEFAULT 5 NOT NULL,
	PRIMARY KEY (offer_id)
) WITHOUT OIDS;


CREATE TABLE categories
(
	category_id int NOT NULL UNIQUE,
	category_name varchar(50) NOT NULL UNIQUE,
	PRIMARY KEY (category_id)
) WITHOUT OIDS;


CREATE TABLE items
(
	item_id serial NOT NULL UNIQUE,
	name varchar(50) NOT NULL UNIQUE,
	description text,
	price decimal NOT NULL,
	balance int,
	category_id int NOT NULL,
	supplier_id int NOT NULL,
	PRIMARY KEY (item_id)
) WITHOUT OIDS;


CREATE TABLE offices
(
	office_id serial NOT NULL,
	address text NOT NULL UNIQUE,
	postcode varchar(6) NOT NULL,
	PRIMARY KEY (office_id)
) WITHOUT OIDS;


CREATE TABLE orders
(
	order_id serial NOT NULL UNIQUE,
	is_payed boolean DEFAULT 'False' NOT NULL,
	total_usd decimal NOT NULL,
	is_given boolean DEFAULT 'False' NOT NULL,
	office_id int NOT NULL,
	username varchar(50) NOT NULL,
	PRIMARY KEY (order_id)
) WITHOUT OIDS;


CREATE TABLE orders_items
(	
	order_id int NOT NULL,
	item_id int NOT NULL
	
) WITHOUT OIDS;


CREATE TABLE suppliers
(
	supplier_id serial NOT NULL UNIQUE,
	company_name varchar(50) NOT NULL,
	address text,
	PRIMARY KEY (supplier_id)
) WITHOUT OIDS;


CREATE TABLE users
(
	user_id serial NOT NULL UNIQUE,
	username varchar(50) NOT NULL UNIQUE,
	full_name varchar(100) NOT NULL,
	email varchar(75) NOT NULL UNIQUE,
	hashed_pass varchar(64) NOT NULL,
	balance_usd decimal DEFAULT 0 NOT NULL,
	user_role varchar(10) DEFAULT 'SHOP_USER' NOT NULL,
	PRIMARY KEY (username)
) WITHOUT OIDS;



ALTER TABLE orders ENABLE ROW LEVEL SECURITY;


/* Create Foreign Keys */

ALTER TABLE items
	ADD FOREIGN KEY (category_id)
	REFERENCES categories (category_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE buy_offers
	ADD FOREIGN KEY (item_id)
	REFERENCES items (item_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE orders_items
	ADD FOREIGN KEY (item_id)
	REFERENCES items (item_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE orders
	ADD FOREIGN KEY (office_id)
	REFERENCES offices (office_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;




ALTER TABLE orders_items
	ADD FOREIGN KEY (order_id)
	REFERENCES orders (order_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE buy_offers
	ADD FOREIGN KEY (supplier_id)
	REFERENCES suppliers (supplier_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE items
	ADD FOREIGN KEY (supplier_id)
	REFERENCES suppliers (supplier_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE orders
	ADD FOREIGN KEY (username)
	REFERENCES users (username)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;



-- TRIGGERS
-- HASH PASSWORD FOR NEW USER

CREATE OR REPLACE FUNCTION hash_password() RETURNS trigger AS
$hash_pass$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    update users set hashed_pass = crypt(new.hashed_pass, gen_salt('bf', 8)) WHERE (username = new.username);
    RETURN new;
END
$hash_pass$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER hash_pass
    after INSERT
    on users
    for each ROW
EXECUTE PROCEDURE hash_password();




-- add item if balance = 0 to buy offer
CREATE OR REPLACE FUNCTION add_zero_b_items_to_offers() RETURNS trigger AS
$zero_item$ 
DECLARE 
BEGIN
	IF (select balance from items where item_id = new.item_id) = 0
	THEN
		INSERT INTO buy_offers(item_id, item_name, supplier_id) 
		VALUES
		(new.item_id, new.name, new.supplier_id);
	END IF;
	RETURN new;
END
$zero_item$ 
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER zero_items
    AFTER UPDATE
    ON items
    FOR EACH ROW
EXECUTE PROCEDURE add_zero_b_items_to_offers();




 

/* INSERT VALUES */

INSERT INTO categories
    (category_id, category_name) 
VALUES 
	(1, 'electronics'),
	(2, 'home'),
	(3, 'clothes'),
	(4, 'other');


INSERT INTO suppliers
    (company_name, address) 
VALUES 
	('ООО Сдаем на пять', 'Большая набережная д.1'),
	('ИП Картавый А.В.', 'Улица Ленина д.5 кв.41'),
	('АО Модная Электроника', 'Трикотажная улица д.7');
	
	
INSERT INTO offices 
	(address, postcode)
VALUES
	('улица Большая ордынка, 4', '210543'),
	('улица первых д.1', '111432'),
	('улица Колхнозническая д.6', '768531');
	
	

INSERT INTO users 
	(username, full_name, email, hashed_pass, balance_usd, user_role)
VALUES
	('jojo', 'ли абраам полоткаев', 'polo@mail.com', 'sec_ret_pas_WoRd', 150, 'SHOP_USER'),
	('bbolq', 'Борис Борисович Сергеев', 'real_borya_2002@ya.ru', 'bobik_bro', 100, 'SHOP_USER'),
	('real_admin', ' Админиев Абубакар', 'abubadm@ua.com', 'pentest_me_plz', 0, 'SHOP_ADMIN'),
	('alez_pro', 'джо джоев', 'email.never_break@mail.com', 'secret_pass', 100, 'SHOP_USER');
	




	
INSERT INTO orders 
	(username, is_payed, total_usd, is_given, office_id)
VALUES
	('alez_pro', False, 23.61, False, 1),
	('jojo', True, 34.15, False, 1),
	('bbolq', False, 12.36, False, 2),
	('alez_pro', True, 4.99, False, 2);





-- policies
-- user can select only his orders
DROP POLICY if exists get_user_orders ON orders;
CREATE POLICY get_user_orders 
    ON orders
    FOR SELECT
    TO SHOP_USER
    USING(
        (SELECT username
         FROM users
         WHERE (username = orders.username)) = current_user
    );
	
	
-- admin can select all orders
DROP POLICY if exists get_admin_orders ON orders;
CREATE POLICY get_admin_orders 
    ON orders
    FOR SELECT
    TO SHOP_ADMIN
    USING(
        true
    );



-- FUNCTIONS
-- authenticate user
CREATE OR REPLACE FUNCTION is_password_correct(_username varchar(50), _password varchar)
	RETURNS boolean AS
	$$
	DECLARE is_password_correct boolean;
	BEGIN
		is_password_correct := users.hashed_pass = crypt(_password, users.hashed_pass) FROM users WHERE users.username = _username;
		RETURN is_password_correct ;
		
	END
	$$ LANGUAGE plpgsql;


-- add random items 
CREATE OR REPLACE PROCEDURE generate_random_items()
AS
$$
	DECLARE
		counter integer;
	BEGIN
	counter := 0;
		FOR i IN 250..2000
			LOOP
				INSERT INTO items 
					(name, description, price, balance, category_id, supplier_id)
				VALUES
					('not nike model ' || i, 'any decription that u want', counter%33+3.49, counter%5+1, 3, counter%3+1);
					counter := counter + 1;
			END LOOP;
			
		FOR i IN 50..1000
			LOOP
				INSERT INTO items 
					(name, description, price, balance, category_id, supplier_id)
				VALUES
					('adidas replica shoes ' || i, 'cool adidas description...', counter%33+0.99, counter%5+1, 3, counter%3+1);
					counter := counter + 1;
			END LOOP;
	END;
$$ LANGUAGE plpgsql;
CALL generate_random_items();




-- TRANSACTION
CREATE OR REPLACE PROCEDURE pay_for_order(_username varchar(50), _order_id int) 
AS $$
	DECLARE
		c       record;
	BEGIN
	
		IF (SELECT is_payed from orders where order_id = _order_id) IS true
		THEN
			RAISE EXCEPTION 'order % already payed', _order_id
      		USING HINT = 'user dont need to pay anymore';
			ROLLBACK;
		ELSE
			COMMIT;
		END IF;	
	
		UPDATE orders SET is_payed=True where order_id = _order_id;
		UPDATE users SET balance_usd = (balance_usd - (SELECT total_usd from orders 
																		where username = _username and
															   				  order_id = _order_id))
						where username = _username;	
						
		FOR c IN SELECT * FROM orders_items WHERE order_id = _order_id
        LOOP
			UPDATE items SET balance = (balance-1) WHERE c.item_id = item_id;
        END LOOP;
		
		IF (SELECT balance_usd from users where username = _username) < 0
		THEN
			RAISE EXCEPTION 'low balance user %', _username
      		USING HINT = 'Please pay buy cash or make deposit to balance';
			ROLLBACK;
		ELSE
			COMMIT;
		END IF;	
		
	END;
$$
language plpgsql;





-- VIEW TOP 5 richest users in the SHOP
CREATE OR REPLACE VIEW richest_user_view 
AS
	SELECT username, balance_usd
	FROM users
	ORDER BY balance_usd DESC
	limit 5;




DROP INDEX IF EXISTS ind_usernames_users;
DROP INDEX IF EXISTS ind_usernames_orders;
DROP INDEX IF EXISTS ind_name_items;

CREATE INDEX ind_usernames_users on users(username);
CREATE INDEX ind_usernames_orders on orders(username);

-- index for 500-1000 values
CREATE INDEX ind_name_items on items(name);



-- asdasdasd