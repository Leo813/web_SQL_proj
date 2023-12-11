create database final_test;
use final_test;

create table customer
    (customer_id        int(7) AUTO_INCREMENT,
     password             varchar(100),
     phone_num          varchar(10),
     email                     varchar(30),
     name                     varchar(15),
     payment		varchar(16),
     primary key (customer_id)
    ) ENGINE=INNODB;

create table meal
    (m_id        varchar(4),
     m_type         varchar(100),
     price        numeric(4),
     primary key (m_id)
    ) ENGINE=INNODB;

create table spa
    (s_id        varchar(4),
     s_type       varchar(100),
     price        numeric(4),
     primary key (s_id)
    ) ENGINE=INNODB;

create table gym_class
    (g_id        varchar(3),
     name       varchar(100),
     price        numeric(4),
     primary key (g_id)
    ) ENGINE=INNODB;

create table room
    (r_id         varchar(4),
     r_type     varchar(100),
     primary key (r_id)
    ) ENGINE=INNODB;

create table opinion
   (opinion_id    int(7) AUTO_INCREMENT,
    customer_id int(7),
    content         varchar(1000),
    w_time          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    primary key(opinion_id),
    foreign key (customer_id) references customer(customer_id)
   ) ENGINE=INNODB;

create table manager
   (ma_id       varchar(7),
    password varchar(10),
    email        varchar(30),
    name        varchar(10),
    primary key(ma_id)
   )ENGINE=INNODB;

create table eats
   (eo_id int(7) AUTO_INCREMENT,
    customer_id int(7),
    m_id             varchar(4),
    e_time              datetime,
    section        varchar(20),
   primary key(eo_id),          
   foreign key (customer_id) references customer(customer_id)
     )ENGINE=INNODB;

create table stay
    (so_id int(7) AUTO_INCREMENT,
     customer_id int(7),
     r_id               varchar(4),
     start_time     datetime,
     end_time      datetime,
     primary key(so_id),
      foreign key (customer_id)   references customer(customer_id)
      ) ENGINE=INNODB;

create table takes  
    ( to_id int(7) AUTO_INCREMENT,
      customer_id   int(7),
      g_id        varchar(4),
      t_time        datetime,
      primary key(to_id),
     foreign key (customer_id) references customer(customer_id)
      ) ENGINE=INNODB;

create table uses
    ( uo_id int(7) AUTO_INCREMENT,
      customer_id     int(7),
      s_id          varchar(4),
      u_time          datetime,
      section        varchar(20),
      primary key(uo_id),
      foreign key (customer_id) references customer(customer_id)
    ) ENGINE=INNODB;


INSERT INTO room(r_id, r_type) values("r001", "Fairmont Gold Room");
INSERT INTO room(r_id, r_type) values("r002", "Samurai Room");
INSERT INTO room(r_id, r_type) values("r003", "Otaku Single Room");
INSERT INTO meal(m_id, m_type, price) values("m001", "Western Style", 500);
INSERT INTO meal(m_id, m_type, price) values("m002", "Chinese Style", 400);
INSERT INTO meal(m_id, m_type, price) values("m003", "Japanese Style", 700);
INSERT INTO spa(s_id, s_type, price) values("s001", "Private Massage", 500);
INSERT INTO spa(s_id, s_type, price) values("s002", "Luxury Massage", 200);
INSERT INTO spa(s_id, s_type, price) values("s003", "Korean Style Spa", 100);