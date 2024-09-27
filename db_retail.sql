-- --------------------------------------------------------
-- Host:                         localhost
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for db_retail
CREATE DATABASE IF NOT EXISTS `db_retail` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `db_retail`;

-- Dumping structure for procedure db_retail.sp_get_all_detail_transaksi
DELIMITER //
CREATE PROCEDURE `sp_get_all_detail_transaksi`()
BEGIN
	SELECT
		tr.id_detail_transaksi,
		tr.id_transaksi,
		k.name_kategori,
		s.name_subkategori,
		p.name_produk,
		p.price_produk,
		tr.quantity_produk
	FROM
		tb_detail_transaksi tr
	LEFT JOIN
		tb_produk p ON p.id_produk = tr.id_produk
	LEFT JOIN
		tb_kategori k ON p.id_kategori = k.id_kategori
	LEFT JOIN
		tb_subkategori s ON p.id_subkategori = s.id_subkategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_histori_transaksi
DELIMITER //
CREATE PROCEDURE `sp_get_all_histori_transaksi`()
BEGIN
    -- Ambil data transaksi
    SELECT
        tr.id_transaksi,
        tr.id_pengguna,
        u.name_pengguna,
        p.name_pelanggan,
        tr.quantity_transaksi,
        tr.total_payment,
        tr.total_price,
        tr.total_change,
        tr.date_transaksi
    FROM
        tb_transaksi tr
    LEFT JOIN
        tb_pengguna u ON tr.id_pengguna = u.id_pengguna
    LEFT JOIN
        tb_pelanggan p ON tr.id_pelanggan = p.id_pelanggan;

END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_kategori
DELIMITER //
CREATE PROCEDURE `sp_get_all_kategori`()
BEGIN
	SELECT 
	sk.id_subkategori,
	tk.id_kategori,
	tk.name_kategori,
	sk.name_subkategori,
	tk.created_at AS katcreated_at,
	tk.updated_at AS katupdated_at,
	sk.created_at AS subkatcreated_at,
	sk.updated_at AS subkatupdated_at
	FROM tb_subkategori sk
	LEFT JOIN tb_kategori tk ON tk.id_kategori = sk.id_subkategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_laporan_stok
DELIMITER //
CREATE PROCEDURE `sp_get_all_laporan_stok`()
BEGIN
	SELECT 
		st.id_stok,
		pr.name_produk,
		st.semula_stok,
		st.quantity_stok,
		st.source_stok,
		st.date_stok
	FROM
	tb_stok st
	LEFT JOIN 
	tb_produk pr ON pr.id_produk = st.id_produk;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_mainkategori
DELIMITER //
CREATE PROCEDURE `sp_get_all_mainkategori`()
BEGIN
	SELECT * FROM tb_kategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_pemasok
DELIMITER //
CREATE PROCEDURE `sp_get_all_pemasok`()
BEGIN
	SELECT
		p.id_pemasok,
		p.name_pemasok,
		p.contact_pemasok,
		p.address_pemasok,
		p.created_at,
		p.updated_at
	FROM
		tb_pemasok p;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_pengguna
DELIMITER //
CREATE PROCEDURE `sp_get_all_pengguna`()
BEGIN
	SELECT
		p.id_pengguna,
		p.name_pengguna,
		p.username_pengguna,
		p.password_pengguna,
		p.role_pengguna,
		p.created_at,
		p.updated_at
	FROM
		tb_pengguna p;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_product
DELIMITER //
CREATE PROCEDURE `sp_get_all_product`()
BEGIN
	SELECT
		p.id_produk,
		p.id_kategori,
		p.id_subkategori,
		k.name_kategori,
		s.name_subkategori,
		p.name_produk,
		p.price_produk,
		p.stock_produk,
		p.created_at,
		p.updated_at
	FROM 
		tb_produk p
	LEFT JOIN
		tb_kategori k ON p.id_kategori = k.id_kategori
	LEFT JOIN
		tb_subkategori s ON p.id_subkategori = s.id_subkategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_all_subkategori
DELIMITER //
CREATE PROCEDURE `sp_get_all_subkategori`()
BEGIN
	SELECT * FROM tb_subkategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_log_aktifitas
DELIMITER //
CREATE PROCEDURE `sp_get_log_aktifitas`()
BEGIN
	SELECT
		la.id_log,
		la.id_pengguna,
		pe.name_pengguna,
		la.activity_log,
		la.date_log
	FROM
		tb_log_aktivitas la
	LEFT JOIN
		tb_pengguna pe ON pe.id_pengguna = la.id_pengguna;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_get_pengguna_histrori_transaksi
DELIMITER //
CREATE PROCEDURE `sp_get_pengguna_histrori_transaksi`(
	IN `p_id_pengguna` VARCHAR(50)
)
BEGIN
    DECLARE v_status VARCHAR(50);
    DECLARE v_message VARCHAR(50);

    -- Cek apakah p_id_pengguna ada di tb_pengguna
    IF NOT EXISTS (SELECT 1 FROM tb_pengguna WHERE id_pengguna = p_id_pengguna) THEN
        -- Jika p_id_pengguna tidak ditemukan di tb_pengguna
        SELECT 'failed' AS status_get, 'ID Tidak Ditemukan' AS message_get;
    
    -- Cek apakah p_id_pengguna ada di tb_pengguna tapi tidak memiliki transaksi di tb_transaksi
    ELSEIF NOT EXISTS (SELECT 1 FROM tb_transaksi WHERE id_pengguna = p_id_pengguna) THEN
        -- Jika p_id_pengguna tidak memiliki transaksi
        SELECT 'failed' AS status_get, 'ID Tidak Memiliki Transaksi' AS message_get;
    
    ELSE
        -- Set status berhasil jika pengguna ditemukan dan memiliki transaksi
        SET v_status = 'success';
        SET v_message = 'Berhasil Mendapatkan Data Transaksi'; -- Tidak ada pesan error jika sukses

        -- Lakukan query untuk transaksi
        SELECT
            t.id_transaksi,
            t.id_pengguna,
            pg.name_pengguna,
            pe.name_pelanggan,
            t.quantity_transaksi,
            t.total_payment,
            t.total_price,
            t.total_change,
            t.date_transaksi,
            v_status AS status_get,
				v_message AS message_get     -- Tambahkan status di hasil query
        FROM
            tb_transaksi t
        LEFT JOIN 
            tb_pelanggan pe ON pe.id_pelanggan = t.id_pelanggan
        LEFT JOIN 
            tb_pengguna pg ON pg.id_pengguna = t.id_pengguna
        WHERE
            t.id_pengguna = p_id_pengguna;

    END IF;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_kategori_add
DELIMITER //
CREATE PROCEDURE `sp_kategori_add`(
	IN `p_nama_kategori` VARCHAR(50)
)
BEGIN
	INSERT INTO tb_kategori
		(name_kategori)
	VALUES 
		(p_nama_kategori);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_kategori_delete
DELIMITER //
CREATE PROCEDURE `sp_kategori_delete`(
	IN `p_id_kategori` INT
)
BEGIN
	DELETE FROM tb_kategori
	WHERE id_kategori = p_id_kategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_kategori_edit
DELIMITER //
CREATE PROCEDURE `sp_kategori_edit`(
	IN `p_id_kategori` INT,
	IN `p_nama_kategori` VARCHAR(50)
)
BEGIN
	UPDATE tb_kategori
	SET name_kategori = p_nama_kategori
	WHERE id_kategori = p_id_kategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_laporanstok_add
DELIMITER //
CREATE PROCEDURE `sp_laporanstok_add`(
	IN `p_id_produk` INT,
	IN `p_stok_semula` INT,
	IN `p_perubahan_stok` INT,
	IN `p_aksi_stok` ENUM('penerimaan','penjualan')
)
BEGIN
	INSERT INTO tb_stok
		(id_produk, semula_stok, quantity_stok, source_stok)
	VALUES 
		(p_id_produk, p_stok_semula, p_perubahan_stok, p_aksi_stok);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_laporanstok_delete
DELIMITER //
CREATE PROCEDURE `sp_laporanstok_delete`(
	IN `p_id_stok` INT
)
BEGIN
	DELETE FROM tb_stok
	WHERE id_stok = p_id_stok;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_login_retiel
DELIMITER //
CREATE PROCEDURE `sp_login_retiel`(
	IN `p_username_login` VARCHAR(100),
	IN `p_password_login` VARCHAR(50)
)
BEGIN
        DECLARE v_stored_password VARCHAR(255);
        DECLARE v_status VARCHAR(255);
    -- Cek apakah username ada di tb_pengguna
    -- Cek apakah username ada di tb_pengguna
    IF NOT EXISTS (SELECT 1 FROM tb_pengguna WHERE username_pengguna = p_username_login) THEN
        -- Jika username tidak ditemukan
        SELECT 'failed' AS v_status, 'Username Tidak Ditemukan' AS v_error_message;
    ELSE
        -- Ambil password yang tersimpan untuk username yang ditemukan
        SELECT password_pengguna INTO v_stored_password FROM tb_pengguna WHERE username_pengguna = p_username_login;
        
        -- Cek apakah password cocok
        IF v_stored_password != p_password_login THEN
            -- Jika password salah
            SELECT 'failed' AS v_status, 'Password Salah' AS v_error_message;
        ELSE
            -- Jika login berhasil, ambil data pengguna dan kembalikan hasilnya
            SELECT 
                id_pengguna, 
                name_pengguna, 
                username_pengguna, 
                role_pengguna, 
                created_at, 
                updated_at,
                'success' AS v_status
            FROM 
                tb_pengguna 
            WHERE 
                username_pengguna = p_username_login;
        END IF;
    END IF;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_log_add
DELIMITER //
CREATE PROCEDURE `sp_log_add`(
	IN `p_id_pengguna` INT,
	IN `p_aksi_aktifitas` TEXT
)
BEGIN
	INSERT INTO tb_log_aktifitas
		(id_pengguna, activity_log)
	VALUES
		(p_id_pengguna, p_aksi_aktifitas);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_log_delete
DELIMITER //
CREATE PROCEDURE `sp_log_delete`(
	IN `p_id_log` INT
)
BEGIN
	DELETE FROM tb_log_aktifitas
	WHERE id_log = p_id_log;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pelanggan_add
DELIMITER //
CREATE PROCEDURE `sp_pelanggan_add`(
	IN `p_nama_pelanggan` VARCHAR(255),
	IN `p_kontak_pelanggan` VARCHAR(50),
	IN `p_alamat_pelanggan` TEXT
)
BEGIN
	INSERT INTO tb_pelanggan
		(name_pelanggan, contact_pelanggan, address_pelanggan, loyalty_points)
	VALUES 
		(p_nama_pelanggan, p_kontak_pelanggan, p_alamat_pelanggan, 0);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pelanggan_delete
DELIMITER //
CREATE PROCEDURE `sp_pelanggan_delete`(
	IN `p_id_pelanggan` INT
)
BEGIN
	DELETE FROM tb_pelanggan
	WHERE id_pelanggan = p_id_pelanggan;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pelanggan_edit
DELIMITER //
CREATE PROCEDURE `sp_pelanggan_edit`(
	IN `p_id_pelanggan` INT,
	IN `p_nama_pelanggan` VARCHAR(255),
	IN `p_kontak_pelanggan` VARCHAR(50),
	IN `p_alamat_pelanggan` TEXT
)
BEGIN
	UPDATE tb_pelanggan
	SET
		name_pelanggan = p_nama_pelanggan,
		contact_pelanggan = p_kontak_pelanggan,
		address_pelanggan = p_alamat_pelanggan
	WHERE id_pelanggan = p_id_pelanggan;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pemasok_add
DELIMITER //
CREATE PROCEDURE `sp_pemasok_add`(
	IN `p_nama_pemasok` VARCHAR(255),
	IN `p_kontak_pemasok` VARCHAR(50),
	IN `p_alamat_pemasok` TEXT
)
BEGIN
	INSERT INTO tb_pemasok
		(name_pemasok, contact_pemasok, address_pemasok)
	VALUES
		(p_nama_pemasok, p_kontak_pemasok, p_alamat_pemasok);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pemasok_delete
DELIMITER //
CREATE PROCEDURE `sp_pemasok_delete`(
	IN `p_id_pemasok` INT
)
BEGIN
	DELETE FROM tb_pemasok
	WHERE id_pemasok = p_id_pemasok;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pemasok_edit
DELIMITER //
CREATE PROCEDURE `sp_pemasok_edit`(
	IN `p_id_pemasok` INT,
	IN `p_nama_pemasok` VARCHAR(255),
	IN `p_kontak_pemasok` VARCHAR(50),
	IN `p_alamat_pemasok` TEXT
)
BEGIN
	UPDATE tb_pemasok
	SET
		name_pemasok = p_nama_pemasok,
		contact_pemasok = p_kontak_pemasok,
		address_pemasok = p_alamat_pemasok
	WHERE id_pemasok = p_id_pemasok;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pengguna_add
DELIMITER //
CREATE PROCEDURE `sp_pengguna_add`(
	IN `p_nama_pengguna` VARCHAR(255),
	IN `p_username_pengguna` VARCHAR(255),
	IN `p_password_pengguna` TEXT,
	IN `p_role_pengguna` ENUM('admin','kasir','manajer')
)
BEGIN
	INSERT INTO tb_pengguna
		(name_pengguna, username_pengguna, password_pengguna, role_pengguna)
	VALUES
		(p_nama_pengguna, p_username_pengguna, p_password_pengguna, p_role_pengguna);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pengguna_delete
DELIMITER //
CREATE PROCEDURE `sp_pengguna_delete`(
	IN `p_id_pengguna` INT
)
BEGIN
	DELETE FROM tb_pengguna
	WHERE id_pengguna = p_id_pengguna;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_pengguna_edit
DELIMITER //
CREATE PROCEDURE `sp_pengguna_edit`(
	IN `p_id_pengguna` INT,
	IN `p_nama_pengguna` VARCHAR(255),
	IN `p_username_pengguna` VARCHAR(255),
	IN `p_password_pengguna` TEXT,
	IN `p_role_pengguna` ENUM('admin','kasir','manajer')
)
BEGIN
	UPDATE tb_pengguna
	SET
		name_pengguna = p_nama_pengguna,
		username_pengguna = p_username_pengguna,
		password_pengguna = p_password_pengguna,
		role_pengguna = p_role_pengguna
	WHERE id_pengguna = p_id_pengguna;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_produk_add
DELIMITER //
CREATE PROCEDURE `sp_produk_add`(
	IN `p_nama_kategori` VARCHAR(50),
	IN `p_nama_subkategori` VARCHAR(50),
	IN `p_nama_produk` VARCHAR(255),
	IN `p_harga_produk` DECIMAL(10,0)
)
BEGIN
    DECLARE v_id_kategori INT;
    DECLARE v_id_subkategori INT;

    -- Mencari id_kategori berdasarkan nama kategori
    SELECT id_kategori INTO v_id_kategori
    FROM tb_kategori
    WHERE name_kategori = p_nama_kategori
    LIMIT 1;  -- Pastikan hanya mengambil satu id_kategori
    
    -- Mencari id_kategori berdasarkan nama kategori
    SELECT id_subkategori INTO v_id_subkategori
    FROM tb_subkategori
    WHERE name_subkategori = p_nama_subkategori
    LIMIT 1;  -- Pastikan hanya mengambil satu id_kategori

    -- Memastikan id_kategori ditemukan
    IF v_id_kategori IS NOT NULL THEN
        -- Melakukan INSERT ke tb_produk
        INSERT INTO tb_produk
            (id_kategori, id_subkategori, name_produk, price_produk, stock_produk)
        VALUES 
            (v_id_kategori, v_id_subkategori, p_nama_produk, p_harga_produk, 0);
    ELSE
        -- Menangani kasus jika kategori tidak ditemukan
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Kategori tidak ditemukan';
    END IF;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_produk_delete
DELIMITER //
CREATE PROCEDURE `sp_produk_delete`(
	IN `p_id_produk` INT
)
BEGIN
	DELETE FROM tb_produk
	WHERE id_produk = p_id_produk;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_produk_edit
DELIMITER //
CREATE PROCEDURE `sp_produk_edit`(
	IN `p_id_produk` INT,
	IN `p_id_subkategori` INT,
	IN `p_nama_produk` VARCHAR(255),
	IN `p_harga_produk` DECIMAL(10,0),
	IN `p_stok_produk` INT
)
BEGIN
	UPDATE tb_produk
	SET
		id_subkategori = p_id_subkategori,
		name_produk = p_nama_produk,
		price_produk = p_harga_produk,
		stock_produk = p_stok_produk
	WHERE id_produk = p_id_produk;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_subkategori_add
DELIMITER //
CREATE PROCEDURE `sp_subkategori_add`(
	IN `p_id_kategori` INT,
	IN `p_name_subkategori` VARCHAR(50)
)
BEGIN
	INSERT INTO tb_subkategori
		(id_kategori, name_subkategori)
	VALUES
		(p_id_kategori, p_name_subkategori);
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_subkategori_delete
DELIMITER //
CREATE PROCEDURE `sp_subkategori_delete`(
	IN `p_id_subkategori` INT
)
BEGIN
	DELETE FROM tb_subkategori
	WHERE id_subkategori = p_id_subkategori;
END//
DELIMITER ;

-- Dumping structure for procedure db_retail.sp_subkategori_edit
DELIMITER //
CREATE PROCEDURE `sp_subkategori_edit`(
	IN `p_id_subkategori` INT,
	IN `p_nama_subkategori` VARCHAR(50)
)
BEGIN
	UPDATE tb_subkategori
	SET name_subkategori = p_nama_subkategori
	WHERE id_subkategori = p_id_subkategori;
END//
DELIMITER ;

-- Dumping structure for table db_retail.tb_detail_transaksi
CREATE TABLE IF NOT EXISTS `tb_detail_transaksi` (
  `id_detail_transaksi` int NOT NULL AUTO_INCREMENT,
  `id_transaksi` int DEFAULT NULL,
  `id_produk` int DEFAULT NULL,
  `quantity_produk` int DEFAULT NULL,
  `date_transaksi` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id_detail_transaksi`),
  KEY `FK_tb_detail_transaksi_tb_produk` (`id_produk`),
  KEY `FK_tb_detail_transaksi_tb_transaksi` (`id_transaksi`),
  CONSTRAINT `FK_tb_detail_transaksi_tb_produk` FOREIGN KEY (`id_produk`) REFERENCES `tb_produk` (`id_produk`),
  CONSTRAINT `FK_tb_detail_transaksi_tb_transaksi` FOREIGN KEY (`id_transaksi`) REFERENCES `tb_transaksi` (`id_transaksi`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table database yang menyimpan detail lengkap dari setiap transaksi (nama produk, jumlah produk, harga produk)';

-- Dumping data for table db_retail.tb_detail_transaksi: ~4 rows (approximately)
INSERT INTO `tb_detail_transaksi` (`id_detail_transaksi`, `id_transaksi`, `id_produk`, `quantity_produk`, `date_transaksi`) VALUES
	(1, 1, 1, 1, '2024-09-09 03:59:15'),
	(2, 1, 2, 1, '2024-09-09 03:59:15'),
	(3, 2, 2, 1, '2024-09-09 03:59:15'),
	(4, 2, 2, 1, '2024-09-09 03:59:15');

-- Dumping structure for table db_retail.tb_kategori
CREATE TABLE IF NOT EXISTS `tb_kategori` (
  `id_kategori` int NOT NULL AUTO_INCREMENT,
  `name_kategori` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_kategori`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Data Utama Kategori';

-- Dumping data for table db_retail.tb_kategori: ~1 rows (approximately)
INSERT INTO `tb_kategori` (`id_kategori`, `name_kategori`, `created_at`, `updated_at`) VALUES
	(1, 'Atasan', '2024-09-04 04:46:54', '2024-09-04 04:46:54'),
	(2, 'Bawahan', '2024-09-04 04:47:11', '2024-09-04 04:47:11');

-- Dumping structure for table db_retail.tb_laporan_keuangan
CREATE TABLE IF NOT EXISTS `tb_laporan_keuangan` (
  `id_laporan` int NOT NULL AUTO_INCREMENT,
  `id_transaksi` int DEFAULT NULL,
  `type_laporan` enum('laba','rugi') NOT NULL,
  `amount_laporan` decimal(10,2) NOT NULL,
  `date_laporan` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_laporan`),
  KEY `id_transaksi` (`id_transaksi`),
  CONSTRAINT `tb_laporan_keuangan_ibfk_1` FOREIGN KEY (`id_transaksi`) REFERENCES `tb_transaksi` (`id_transaksi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Laporan Keungan Termasuk Laba dan Rugi';

-- Dumping data for table db_retail.tb_laporan_keuangan: ~0 rows (approximately)

-- Dumping structure for table db_retail.tb_log_aktivitas
CREATE TABLE IF NOT EXISTS `tb_log_aktivitas` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `id_pengguna` int DEFAULT NULL,
  `activity_log` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `date_log` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_log`),
  KEY `id_pengguna` (`id_pengguna`),
  CONSTRAINT `tb_log_aktivitas_ibfk_1` FOREIGN KEY (`id_pengguna`) REFERENCES `tb_pengguna` (`id_pengguna`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Aktifitas Pengguna';

-- Dumping data for table db_retail.tb_log_aktivitas: ~2 rows (approximately)
INSERT INTO `tb_log_aktivitas` (`id_log`, `id_pengguna`, `activity_log`, `date_log`) VALUES
	(1, 1, 'Add Item to Product', '2024-09-04 04:51:19'),
	(2, 1, 'Transaction', '2024-09-09 01:14:27');

-- Dumping structure for table db_retail.tb_pelanggan
CREATE TABLE IF NOT EXISTS `tb_pelanggan` (
  `id_pelanggan` int NOT NULL AUTO_INCREMENT,
  `name_pelanggan` varchar(255) NOT NULL,
  `contact_pelanggan` varchar(255) DEFAULT NULL,
  `address_pelanggan` text,
  `loyalty_points` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pelanggan`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Data Pelanggan (Member) dan Diperlukan Register';

-- Dumping data for table db_retail.tb_pelanggan: ~0 rows (approximately)
INSERT INTO `tb_pelanggan` (`id_pelanggan`, `name_pelanggan`, `contact_pelanggan`, `address_pelanggan`, `loyalty_points`, `created_at`, `updated_at`) VALUES
	(1, 'Non-Member', '081210295730', 'Bandung, Jawa Barat', 1, '2024-09-04 04:48:59', '2024-09-04 04:48:59');

-- Dumping structure for table db_retail.tb_pemasok
CREATE TABLE IF NOT EXISTS `tb_pemasok` (
  `id_pemasok` int NOT NULL AUTO_INCREMENT,
  `name_pemasok` varchar(255) NOT NULL,
  `contact_pemasok` varchar(255) DEFAULT NULL,
  `address_pemasok` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pemasok`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Data Pemasok (Supplier)';

-- Dumping data for table db_retail.tb_pemasok: ~0 rows (approximately)
INSERT INTO `tb_pemasok` (`id_pemasok`, `name_pemasok`, `contact_pemasok`, `address_pemasok`, `created_at`, `updated_at`) VALUES
	(1, 'Disclose', '081234567832', 'Kopo, Bandung', '2024-09-04 04:50:03', '2024-09-23 04:44:42');

-- Dumping structure for table db_retail.tb_pengguna
CREATE TABLE IF NOT EXISTS `tb_pengguna` (
  `id_pengguna` int NOT NULL AUTO_INCREMENT,
  `name_pengguna` varchar(255) NOT NULL,
  `username_pengguna` varchar(255) NOT NULL,
  `password_pengguna` varchar(255) NOT NULL,
  `role_pengguna` enum('admin','kasir','manajer') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pengguna`),
  UNIQUE KEY `username_pengguna` (`username_pengguna`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Data Pengguna (Admin, Petugas, Manajer)';

-- Dumping data for table db_retail.tb_pengguna: ~3 rows (approximately)
INSERT INTO `tb_pengguna` (`id_pengguna`, `name_pengguna`, `username_pengguna`, `password_pengguna`, `role_pengguna`, `created_at`, `updated_at`) VALUES
	(1, 'Admin Putra', 'admin', 'bced6fd149cfcdb85741768da12e41c6', 'admin', '2024-09-04 04:44:24', '2024-09-23 02:56:08'),
	(2, 'Kasir Putra', 'kasir', '1bd555d23697f9f6923c753337616333', 'kasir', '2024-09-04 04:45:01', '2024-09-23 02:56:27'),
	(3, 'Manajer Putra', 'manajer', '29a39d4c826e68d0a7c62e791f5bb780', 'manajer', '2024-09-04 04:45:33', '2024-09-23 03:02:24');

-- Dumping structure for table db_retail.tb_produk
CREATE TABLE IF NOT EXISTS `tb_produk` (
  `id_produk` int NOT NULL AUTO_INCREMENT,
  `name_produk` varchar(255) NOT NULL,
  `price_produk` decimal(10,0) NOT NULL,
  `stock_produk` int NOT NULL,
  `id_kategori` int DEFAULT NULL,
  `id_subkategori` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_produk`),
  KEY `id_kategori` (`id_kategori`),
  KEY `id_subkategori` (`id_subkategori`),
  CONSTRAINT `tb_produk_ibfk_1` FOREIGN KEY (`id_kategori`) REFERENCES `tb_kategori` (`id_kategori`),
  CONSTRAINT `tb_produk_ibfk_2` FOREIGN KEY (`id_subkategori`) REFERENCES `tb_subkategori` (`id_subkategori`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Data Produk Secara Lengkap';

-- Dumping data for table db_retail.tb_produk: ~18 rows (approximately)
INSERT INTO `tb_produk` (`id_produk`, `name_produk`, `price_produk`, `stock_produk`, `id_kategori`, `id_subkategori`, `created_at`, `updated_at`) VALUES
	(1, 'Jaket Hitam', 299999, 6, 1, 1, '2024-09-04 04:51:19', '2024-09-27 06:39:14'),
	(2, 'Ripped Jeans Lutut', 499999, 6, 2, 3, '2024-09-04 04:51:58', '2024-09-27 06:39:21'),
	(3, 'Jaket Putih', 299999, 10, 1, 1, '2024-09-23 04:35:10', '2024-09-27 06:22:56');

-- Dumping structure for table db_retail.tb_stok
CREATE TABLE IF NOT EXISTS `tb_stok` (
  `id_stok` int NOT NULL AUTO_INCREMENT,
  `id_produk` int DEFAULT NULL,
  `semula_stok` int DEFAULT NULL,
  `quantity_stok` int NOT NULL,
  `source_stok` enum('penerimaan','penyesuaian','penjualan') NOT NULL,
  `date_stok` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_stok`),
  KEY `id_produk` (`id_produk`),
  CONSTRAINT `tb_stok_ibfk_1` FOREIGN KEY (`id_produk`) REFERENCES `tb_produk` (`id_produk`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Laporan Aktifitas Stok Produk';

-- Dumping data for table db_retail.tb_stok: ~2 rows (approximately)
INSERT INTO `tb_stok` (`id_stok`, `id_produk`, `semula_stok`, `quantity_stok`, `source_stok`, `date_stok`) VALUES
	(1, 1, 2, 3, 'penerimaan', '2024-09-04 04:52:54'),
	(2, 2, 4, 1, 'penjualan', '2024-09-04 04:53:36');

-- Dumping structure for table db_retail.tb_subkategori
CREATE TABLE IF NOT EXISTS `tb_subkategori` (
  `id_subkategori` int NOT NULL AUTO_INCREMENT,
  `name_subkategori` varchar(255) NOT NULL,
  `id_kategori` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_subkategori`),
  KEY `id_kategori` (`id_kategori`),
  CONSTRAINT `tb_subkategori_ibfk_1` FOREIGN KEY (`id_kategori`) REFERENCES `tb_kategori` (`id_kategori`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Data Sub Kategori';

-- Dumping data for table db_retail.tb_subkategori: ~4 rows (approximately)
INSERT INTO `tb_subkategori` (`id_subkategori`, `name_subkategori`, `id_kategori`, `created_at`, `updated_at`) VALUES
	(1, 'Jaket', 1, '2024-09-04 04:47:27', '2024-09-04 04:47:28'),
	(2, 'Sweater', 1, '2024-09-04 04:47:43', '2024-09-04 04:47:43'),
	(3, 'Celana Chinos', 2, '2024-09-04 04:47:57', '2024-09-04 04:52:28'),
	(4, 'Celana Jeans', 2, '2024-09-04 04:48:13', '2024-09-04 04:52:22');

-- Dumping structure for table db_retail.tb_transaksi
CREATE TABLE IF NOT EXISTS `tb_transaksi` (
  `id_transaksi` int NOT NULL AUTO_INCREMENT,
  `id_pelanggan` int DEFAULT NULL,
  `id_pengguna` int DEFAULT NULL,
  `quantity_transaksi` int NOT NULL,
  `total_payment` int DEFAULT NULL,
  `total_price` int NOT NULL DEFAULT '0',
  `total_change` int DEFAULT NULL,
  `date_transaksi` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_transaksi`),
  KEY `id_pelanggan` (`id_pelanggan`),
  KEY `tb_transaksi_ibfk_3` (`id_pengguna`),
  CONSTRAINT `tb_transaksi_ibfk_2` FOREIGN KEY (`id_pelanggan`) REFERENCES `tb_pelanggan` (`id_pelanggan`),
  CONSTRAINT `tb_transaksi_ibfk_3` FOREIGN KEY (`id_pengguna`) REFERENCES `tb_pengguna` (`id_pengguna`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table Database yang Menyimpan Keseluruhan Transaksi';

-- Dumping data for table db_retail.tb_transaksi: ~2 rows (approximately)
INSERT INTO `tb_transaksi` (`id_transaksi`, `id_pelanggan`, `id_pengguna`, `quantity_transaksi`, `total_payment`, `total_price`, `total_change`, `date_transaksi`) VALUES
	(1, 1, 1, 2, 799998, 799998, 0, '2024-09-09 01:14:27'),
	(2, 1, 2, 2, 999998, 999998, 0, '2024-09-09 02:14:27');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
