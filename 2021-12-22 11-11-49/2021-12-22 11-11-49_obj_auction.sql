/*
SQLyog Community v13.1.7 (64 bit)
MySQL - 10.4.13-MariaDB : Database - cellframe
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`cellframe` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `cellframe`;

/*Table structure for table `auction` */

DROP TABLE IF EXISTS `auction`;

CREATE TABLE `auction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `maxRange` int(11) DEFAULT NULL,
  `minScore` int(11) DEFAULT NULL,
  `activeState` int(11) DEFAULT NULL,
  `auctionState` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 ROW_FORMAT=FIXED;

/*Data for the table `auction` */

insert  into `auction`(`id`,`maxRange`,`minScore`,`activeState`,`auctionState`,`created_at`) values 
(1,8,25000,0,0,'2021-12-22 02:54:43'),
(2,8,25000,0,0,'2021-12-22 02:55:33'),
(3,8,25000,0,0,'2021-12-22 03:09:55'),
(4,8,25000,0,0,'2021-12-22 03:10:47'),
(5,8,25000,0,0,'2021-12-22 03:20:53'),
(6,8,25000,0,0,'2021-12-22 03:21:46'),
(7,8,25000,1,0,'2021-12-22 03:21:47'),
(8,8,25000,2,0,'2021-12-22 03:48:04');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
