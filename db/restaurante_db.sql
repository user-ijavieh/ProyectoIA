-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 20-01-2026 a las 12:37:43
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.2.4
create database if not exists restaurante_db;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `restaurante_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `id_pedido` varchar(50) NOT NULL,
  `producto` varchar(100) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `nota` text DEFAULT NULL,
  `estado` varchar(50) DEFAULT 'pendiente',
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id`, `id_pedido`, `producto`, `cantidad`, `nota`, `estado`, `fecha`) VALUES
(1, '7D06BF25', 'Pizza Margarita', 1, 'Sin albahaca', 'completado', '2026-01-15 08:56:03'),
(2, '26A8BF75', 'Hamburguesa Completa', 2, 'Poco hecha', 'completado', '2026-01-15 08:56:03'),
(3, '26A8BF75', 'Sushi Variado', 1, 'Con extra de wasabi', 'completado', '2026-01-15 08:56:03'),
(4, '50BECA03', 'Sushi Variado', 2, 'Con extra de wasabi', 'preparacion', '2026-01-15 08:56:03'),
(5, '50BECA03', 'Hamburguesa Completa', 1, 'Poco hecha', 'pendiente', '2026-01-15 08:56:03'),
(6, '50BECA03', 'Pizza Margarita', 2, 'Sin albahaca', 'preparacion', '2026-01-15 08:56:03'),
(7, '74310ED9', 'Hamburguesa', 2, 'S muy hechas', 'preparacion', '2026-01-15 09:41:11'),
(8, '74310ED9', 'Ensalada', 1, 'Sin notas', 'preparacion', '2026-01-15 09:41:11'),
(9, '9E543DCA', 'Tacos', 5, 'Sin picante', 'completado', '2026-01-15 10:09:01'),
(10, '8CC54634', 'Pasta', 3, 'Pizzas carbonara', 'pendiente', '2026-01-15 12:34:20'),
(11, 'A7439B99', 'Pizza', 2, 'S extra queso', 'preparacion', '2026-01-15 12:36:02'),
(12, '00AAF373', 'Hamburguesa', 3, 'S sin pepinillos', 'preparacion', '2026-01-15 12:38:47'),
(13, '00AAF373', 'Coca cola', 1, 'Cocacola', 'pendiente', '2026-01-15 12:38:47'),
(14, '58089E99', 'Pizza', 1, 'Salami', 'preparacion', '2026-01-15 13:17:12'),
(15, '58089E99', 'Fanta', 1, 'Sin notas', 'preparacion', '2026-01-15 13:17:12');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
