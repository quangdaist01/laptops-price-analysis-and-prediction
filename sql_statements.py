load_dim_cpu_speed = """INSERT INTO dim_cpu_speed (cpu_speed) 
                     SELECT DISTINCT cpu_speed 
                     FROM staging_laptop
                     WHERE cpu_speed NOT IN (SELECT cpu_speed FROM dim_cpu_speed);"""

load_dim_gpu_type = """INSERT INTO dim_gpu_type (gpu_type) 
                    SELECT DISTINCT gpu_type 
                    FROM staging_laptop
                    WHERE gpu_type NOT IN (SELECT gpu_type FROM dim_gpu_type);"""

load_dim_ram_type = """INSERT INTO dim_ram_type (ram_type) 
                    SELECT DISTINCT ram_type 
                    FROM staging_laptop
                    WHERE ram_type NOT IN (SELECT ram_type FROM dim_ram_type);"""

load_dim_ram = """INSERT INTO dim_ram (ram) 
               SELECT DISTINCT ram 
               FROM staging_laptop
               WHERE ram NOT IN (SELECT ram FROM dim_ram);"""

load_dim_ram_speed = """INSERT INTO dim_ram_speed (ram_speed) 
                     SELECT DISTINCT ram_speed 
                     FROM staging_laptop
                     WHERE ram_speed NOT IN (SELECT ram_speed FROM dim_ram_speed);"""

load_dim_storage = """INSERT INTO dim_storage (storage) 
                    SELECT DISTINCT storage 
                    FROM staging_laptop
                    WHERE storage NOT IN (SELECT storage FROM dim_storage);"""

load_dim_screen_size = """INSERT INTO dim_screen_size (screen_size) 
                        SELECT DISTINCT screen_size 
                        FROM staging_laptop
                        WHERE screen_size NOT IN (SELECT screen_size FROM dim_screen_size);"""

load_dim_resolution = """INSERT INTO dim_resolution (resolution) 
                       SELECT DISTINCT resolution 
                       FROM staging_laptop
                       WHERE resolution NOT IN (SELECT resolution FROM dim_resolution);"""

load_dim_material = """INSERT INTO dim_material (material) 
                     SELECT DISTINCT material 
                     FROM staging_laptop
                     WHERE material NOT IN (SELECT material FROM dim_material);"""

load_dim_os = """INSERT INTO dim_os (os) 
               SELECT DISTINCT os 
               FROM staging_laptop
               WHERE os NOT IN (SELECT os FROM dim_os);"""

load_dim_released_year = """INSERT INTO dim_released_year (released_year) 
                           SELECT DISTINCT released_year AS released_year 
                           FROM staging_laptop
                           WHERE released_year NOT IN (SELECT released_year FROM dim_released_year);"""

load_dim_name = """INSERT INTO dim_name (name) 
                  SELECT DISTINCT name 
                  FROM staging_laptop
                  WHERE name NOT IN (SELECT name FROM dim_name);"""

load_dim_warranty = """INSERT INTO dim_warranty (warranty) 
                      SELECT DISTINCT used_warranty 
                      FROM staging_laptop
                      WHERE used_warranty NOT IN (SELECT warranty FROM dim_warranty);
                      INSERT INTO dim_warranty (warranty) 
                      SELECT DISTINCT new_warranty 
                      FROM staging_laptop
                      WHERE new_warranty NOT IN (SELECT warranty FROM dim_warranty);"""

load_dim_brand = """INSERT INTO dim_brand (brand) 
                    SELECT DISTINCT brand 
                    FROM staging_laptop
                    WHERE brand NOT IN (SELECT brand FROM dim_brand);"""

load_fact_laptop = ("""
INSERT INTO fact_laptop (id,
                         cpu_type_id,
                         cpu_speed_id,
                         gpu_type_id,
                         ram_type_id,
                         ram_id,
                         ram_speed_id,
                         storage_id,
                         screen_size_id,
                         resolution_id,
                         material_id,
                         os_id,
                         released_year_id,
                         name_id,
                         used_warranty_id,
                         new_warranty_id,
                         brand_id,
                         weight,
                         thickness,
                         width,
                         length,
                         new_price,
                         used_price,
                         is_sold)
SELECT l.id,
       ct.id  AS cpu_type_id,
       cs.id  AS cpu_speed_id,
       gt.id  AS gpu_type_id,
       rt.id  AS ram_type_id,
       r.id   AS ram_id,
       rs.id  AS ram_speed_id,
       s.id   AS storage_id,
       ss.id  AS screen_size_id,
       res.id AS resolution_id,
       m.id   AS material_id,
       o.id   AS os_id,
       ry.id  AS released_year_id,
       n.id   AS name_id,
       w_used.id   AS used_warranty_id,
       w_new.id   AS new_warranty_id,
       b.id   AS brand_id,
       l.weight,
       l.thickness,
       l.width,
       l.length,
       l.new_price,
       l.used_price,
       CASE sis.status
        WHEN 'I' THEN
          FALSE
        WHEN 'D' THEN
            TRUE
        END id
FROM staging_laptop l
     JOIN dim_cpu_type ct ON l.cpu_type = ct.cpu_type
     JOIN dim_cpu_speed cs ON l.cpu_speed = cs.cpu_speed
     JOIN dim_gpu_type gt ON l.gpu_type = gt.gpu_type
     JOIN dim_ram_type rt ON l.ram_type = rt.ram_type
     JOIN dim_ram r ON l.ram = r.ram
     JOIN dim_ram_speed rs ON l.ram_speed = rs.ram_speed
     JOIN dim_storage s ON l.storage = s.storage
     JOIN dim_screen_size ss ON l.screen_size = ss.screen_size
     JOIN dim_resolution res ON l.resolution = res.resolution
     JOIN dim_material m ON l.material = m.material
     JOIN dim_os o ON l.os = o.os
     JOIN dim_released_year ry ON l.released_year = ry.released_year
     JOIN dim_name n ON l.name = n.name
     JOIN dim_warranty w_used ON l.used_warranty = w_used.warranty
     JOIN dim_warranty w_new ON l.new_warranty = w_new.warranty
     JOIN dim_brand b ON l.brand = b.brand 
     JOIN staging_is_sold sis ON l.id = sis.id;
""")

create_is_sold_table = """
DROP TABLE IF EXISTS public.staging_is_sold CASCADE;
CREATE TABLE staging_is_sold
AS
SELECT s.id, 'I' as status
FROM staging_laptop s
EXCEPT
SELECT f.id, 'I' as status
FROM fact_laptop f
UNION
SELECT f.id, 'D' as status
FROM fact_laptop f
EXCEPT
SELECT s.id, 'D' as status
FROM staging_laptop s;
"""
