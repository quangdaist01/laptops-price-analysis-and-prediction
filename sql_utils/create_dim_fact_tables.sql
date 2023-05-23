CREATE TABLE dim_cpu_type
(
    id       SERIAL PRIMARY KEY,
    cpu_type VARCHAR(255) NOT NULL
);

CREATE TABLE dim_cpu_speed
(
    id        SERIAL PRIMARY KEY,
    cpu_speed FLOAT NOT NULL
);

CREATE TABLE dim_gpu_type
(
    id       SERIAL PRIMARY KEY,
    gpu_type VARCHAR(255) NOT NULL
);

CREATE TABLE dim_ram_type
(
    id       SERIAL PRIMARY KEY,
    ram_type VARCHAR(255) NOT NULL
);

CREATE TABLE dim_ram
(
    id  SERIAL PRIMARY KEY,
    ram DECIMAL NOT NULL
);

CREATE TABLE dim_ram_speed
(
    id        SERIAL PRIMARY KEY,
    ram_speed INT NOT NULL
);

CREATE TABLE dim_storage
(
    id      SERIAL PRIMARY KEY,
    storage VARCHAR(255) NOT NULL
);

CREATE TABLE dim_screen_size
(
    id          SERIAL PRIMARY KEY,
    screen_size FLOAT NOT NULL
);

CREATE TABLE dim_resolution
(
    id         SERIAL PRIMARY KEY,
    resolution VARCHAR(255) NOT NULL
);

CREATE TABLE dim_material
(
    id       SERIAL PRIMARY KEY,
    material VARCHAR(255) NOT NULL
);

CREATE TABLE dim_os
(
    id SERIAL PRIMARY KEY,
    os VARCHAR(255) NOT NULL
);

CREATE TABLE dim_released_year
(
    id            SERIAL PRIMARY KEY,
    released_year INT NOT NULL
);

CREATE TABLE dim_name
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE dim_warranty
(
    id       SERIAL PRIMARY KEY,
    warranty VARCHAR(255) NOT NULL
);

CREATE TABLE dim_brand
(
    id    SERIAL PRIMARY KEY,
    brand VARCHAR(255) NOT NULL
);

CREATE TABLE fact_laptop
(
    id               VARCHAR(255),
    cpu_type_id      INT REFERENCES dim_cpu_type (id),
    cpu_speed_id     INT REFERENCES dim_cpu_speed (id),
    gpu_type_id      INT REFERENCES dim_gpu_type (id),
    ram_type_id      INT REFERENCES dim_ram_type (id),
    ram_id           INT REFERENCES dim_ram (id),
    ram_speed_id     INT REFERENCES dim_ram_speed (id),
    storage_id       INT REFERENCES dim_storage (id),
    screen_size_id   INT REFERENCES dim_screen_size (id),
    resolution_id    INT REFERENCES dim_resolution (id),
    material_id      INT REFERENCES dim_material (id),
    os_id            INT REFERENCES dim_os (id),
    released_year_id INT REFERENCES dim_released_year (id),
    name_id          INT REFERENCES dim_name (id),
    used_warranty_id INT REFERENCES dim_warranty (id),
    new_warranty_id  INT REFERENCES dim_warranty (id),
    brand_id         INT REFERENCES dim_brand (id),
    weight           FLOAT,
    thickness        FLOAT,
    width            FLOAT,
    length           FLOAT,
    new_price        FLOAT,
    used_price       FLOAT,
    is_sold          BOOLEAN
);

