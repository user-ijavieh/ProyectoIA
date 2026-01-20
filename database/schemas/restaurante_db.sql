-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 20-01-2026 a las 15:48:34
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

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
-- Estructura de tabla para la tabla `menu`
--

CREATE TABLE `menu` (
  `id` int(11) NOT NULL,
  `nombre_producto` varchar(100) NOT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `menu`
--

INSERT INTO `menu` (`id`, `nombre_producto`, `precio`, `disponible`) VALUES
(1, 'pizza', 12.50, 1),
(2, 'hamburguesa', 8.90, 1),
(3, 'tacos', 7.50, 1),
(4, 'ensalada', 6.00, 1),
(5, 'zumo', 3.50, 1),
(6, 'pasta', 10.00, 1),
(7, 'pan', 1.50, 1),
(8, 'hot dog', 5.50, 1),
(9, 'refresco', 2.00, 1),
(10, 'coca cola', 2.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `id_pedido` varchar(50) NOT NULL,
  `producto` varchar(100) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `nota` text DEFAULT NULL,
  `estado` varchar(50) DEFAULT 'pendiente',
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id`, `id_pedido`, `producto`, `cantidad`, `precio_unitario`, `nota`, `estado`, `fecha`) VALUES
(1, '7D06BF25', 'Pizza Margarita', 1, NULL, 'Sin albahaca', 'completado', '2026-01-15 08:56:03'),
(2, '26A8BF75', 'Hamburguesa Completa', 2, NULL, 'Poco hecha', 'completado', '2026-01-15 08:56:03'),
(3, '26A8BF75', 'Sushi Variado', 1, NULL, 'Con extra de wasabi', 'completado', '2026-01-15 08:56:03'),
(4, '50BECA03', 'Sushi Variado', 2, NULL, 'Con extra de wasabi', 'preparacion', '2026-01-15 08:56:03'),
(5, '50BECA03', 'Hamburguesa Completa', 1, NULL, 'Poco hecha', 'pendiente', '2026-01-15 08:56:03'),
(6, '50BECA03', 'Pizza Margarita', 2, NULL, 'Sin albahaca', 'preparacion', '2026-01-15 08:56:03'),
(7, '74310ED9', 'Hamburguesa', 2, NULL, 'S muy hechas', 'preparacion', '2026-01-15 09:41:11'),
(8, '74310ED9', 'Ensalada', 1, NULL, 'Sin notas', 'preparacion', '2026-01-15 09:41:11'),
(9, '9E543DCA', 'Tacos', 5, NULL, 'Sin picante', 'completado', '2026-01-15 10:09:01'),
(11, 'A7439B99', 'Pizza', 2, NULL, 'S extra queso', 'preparacion', '2026-01-15 12:36:02'),
(14, '58089E99', 'Pizza', 1, NULL, 'Salami', 'preparacion', '2026-01-15 13:17:12'),
(15, '58089E99', 'Fanta', 1, NULL, 'Sin notas', 'preparacion', '2026-01-15 13:17:12'),
(16, '707A88E5', 'Pizza', 2, 12.50, 'Sin notas', 'preparacion', '2026-01-20 12:59:50'),
(17, '707A88E5', 'Coca cola', 1, 2.00, 'Cocacola', 'preparacion', '2026-01-20 12:59:50');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `menu`
--
ALTER TABLE `menu`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `menu`
--
ALTER TABLE `menu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
