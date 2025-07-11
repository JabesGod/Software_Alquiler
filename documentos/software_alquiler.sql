-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 27-05-2025 a las 21:53:24
-- Versión del servidor: 11.6.2-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `software_alquiler`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_alquiler`
--

CREATE TABLE `alquiler_alquiler` (
  `id` bigint(20) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `precio_total` int(11) NOT NULL,
  `estado_alquiler` varchar(20) NOT NULL,
  `renovacion` tinyint(1) NOT NULL,
  `aprobado_por` varchar(100) DEFAULT NULL,
  `contrato_firmado` tinyint(1) NOT NULL,
  `cliente_id` bigint(20) NOT NULL,
  `equipo_id` bigint(20) NOT NULL,
  `fecha_creacion` datetime(6) DEFAULT NULL,
  `numero_factura` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_alquiler`
--

INSERT INTO `alquiler_alquiler` (`id`, `fecha_inicio`, `fecha_fin`, `precio_total`, `estado_alquiler`, `renovacion`, `aprobado_por`, `contrato_firmado`, `cliente_id`, `equipo_id`, `fecha_creacion`, `numero_factura`) VALUES
(1, '2025-05-10', '2025-06-06', 1, 'finalizado', 0, 'Ignacio Sandoval', 1, 1, 3, '2025-05-26 21:14:16.830385', NULL),
(3, '2026-07-07', '2026-07-07', 10100, 'finalizado', 0, '1010', 1, 3, 8, '2025-05-26 21:14:16.830385', NULL),
(4, '2025-05-10', '2025-10-10', 100000, 'activo', 0, 'Ignacio Sandoval', 1, 2, 8, '2025-05-26 21:14:16.830385', NULL),
(5, '2025-05-10', '2025-10-10', 45120, 'activo', 0, 'Ignacio Sandoval', 1, 2, 6, '2025-05-26 21:14:16.830385', NULL),
(6, '2025-05-23', '2026-05-23', 100000, 'activo', 0, '520', 1, 1, 21, '2025-05-26 21:14:16.830385', NULL),
(7, '2025-06-30', '2026-06-30', 3000000, 'activo', 0, 'Chayanne', 0, 3, 2, '2025-05-26 21:14:16.830385', NULL),
(8, '2025-05-10', '2025-05-27', 300000, 'activo', 0, 'Ignacio Sandoval', 1, 2, 2, '2025-05-26 21:14:16.830385', NULL),
(9, '2025-05-24', '2025-05-27', 91201250, 'activo', 0, 'Chayanne', 0, 1, 21, '2025-05-26 21:14:16.830385', NULL),
(10, '2025-05-24', '2025-05-27', 120845120, 'activo', 0, 'Chayanne', 0, 1, 21, '2025-05-26 21:14:16.830385', NULL),
(11, '2025-05-10', '2025-05-29', 785402, 'activo', 1, 'Chayanne', 1, 1, 18, '2025-05-26 21:14:16.830385', NULL),
(12, '2025-05-10', '2025-05-19', 8754120, 'activo', 0, 'Chayanne', 0, 3, 19, '2025-05-26 21:14:16.830385', NULL),
(13, '2025-05-10', '2025-05-28', 896502, 'activo', 0, 'Chayanne', 0, 2, 21, '2025-05-26 21:14:16.830385', NULL),
(14, '2025-05-10', '2025-05-25', 520, 'activo', 0, 'Ignacio Sandoval', 1, 2, 1, '2025-05-26 21:14:16.830385', NULL),
(15, '2020-05-10', '2025-05-27', 645130, 'activo', 0, 'Chayanne', 0, 1, 21, '2025-05-26 21:41:37.322920', '1020');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_cliente`
--

CREATE TABLE `alquiler_cliente` (
  `id` bigint(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `direccion` longtext NOT NULL,
  `informacion_facturacion` longtext DEFAULT NULL,
  `estado_verificacion` varchar(20) NOT NULL,
  `documento_rut` varchar(100) DEFAULT NULL,
  `documento_cedula` varchar(100) DEFAULT NULL,
  `contrato_firmado` varchar(100) DEFAULT NULL,
  `barrio` varchar(50) DEFAULT NULL,
  `ciudad` varchar(50) DEFAULT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `fecha_creacion` datetime(6) DEFAULT NULL,
  `metodo_pago_preferido` varchar(30) DEFAULT NULL,
  `nit` varchar(20) DEFAULT NULL,
  `nombre_empresa` varchar(100) DEFAULT NULL,
  `numero_documento` varchar(50) DEFAULT NULL,
  `tipo_cliente` varchar(10) NOT NULL,
  `tipo_documento` varchar(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_cliente`
--

INSERT INTO `alquiler_cliente` (`id`, `nombre`, `email`, `telefono`, `direccion`, `informacion_facturacion`, `estado_verificacion`, `documento_rut`, `documento_cedula`, `contrato_firmado`, `barrio`, `ciudad`, `fecha_actualizacion`, `fecha_creacion`, `metodo_pago_preferido`, `nit`, `nombre_empresa`, `numero_documento`, `tipo_cliente`, `tipo_documento`) VALUES
(1, 'Cliente de prueba', 'marketing@tecnonacho.com', '123456789', 'Calle falsa 123', '', 'verificado', '', '', '', NULL, NULL, '2025-05-27 13:50:49.946859', '2025-05-26 16:52:49.131147', NULL, NULL, NULL, NULL, 'natural', 'CC'),
(2, 'Cliente de prueba', 'comunicacionestecnonacho@gmail.com', '123456789', 'Calle falsa 123', '', 'verificado', '', '', '', NULL, NULL, '2025-05-27 13:48:53.036932', '2025-05-26 16:52:49.131147', NULL, NULL, NULL, NULL, 'natural', 'CC'),
(3, 'Cliente', 'jabesrko011@gmail.com', '123456789', 'Calle falsa 123', NULL, 'verificado', '', '', '', NULL, NULL, '2025-05-26 16:52:48.998727', '2025-05-26 16:52:49.131147', NULL, NULL, NULL, NULL, 'natural', 'CC');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_contrato`
--

CREATE TABLE `alquiler_contrato` (
  `id` bigint(20) NOT NULL,
  `fecha_contratacion` date NOT NULL,
  `terminos_contrato` longtext NOT NULL,
  `fecha_firma` date DEFAULT NULL,
  `firma_cliente` varchar(100) DEFAULT NULL,
  `documento_contrato` varchar(100) NOT NULL,
  `alquiler_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_contrato`
--

INSERT INTO `alquiler_contrato` (`id`, `fecha_contratacion`, `terminos_contrato`, `fecha_firma`, `firma_cliente`, `documento_contrato`, `alquiler_id`) VALUES
(1, '2025-05-17', '\n    Contrato de alquiler entre Cliente de prueba y la empresa.\n    Equipo: HP a (Serie: aaa)\n    Desde 2025-05-10 hasta 2025-06-06.\n    Precio total: $1.00.\n    ', '2025-05-17', 'firmas/firma_1_bknUIwm.png', 'contratos/contrato_alquiler_1_m31NOLM.pdf', 1),
(3, '2025-05-22', '\n    Contrato de alquiler entre Cliente y la empresa.\n    Equipo: HP a (Serie: aaaaaaaa)\n    Desde 2026-07-07 hasta 2026-07-07.\n    Precio total: $10100.00.\n    ', '2025-05-22', 'firmas/cropped-faviconong.webp', 'contratos/contrato_alquiler_3.pdf', 3),
(4, '2025-05-23', '\n    Contrato de alquiler entre Cliente de prueba y la empresa.\n    Equipo: HP a (Serie: aaaaaaaa)\n    Desde 2025-05-10 hasta 2025-10-10.\n    Precio total: $100000.00.\n    ', NULL, '', 'contratos/contrato_alquiler_4.pdf', 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_equipo`
--

CREATE TABLE `alquiler_equipo` (
  `id` bigint(20) NOT NULL,
  `marca` varchar(50) NOT NULL,
  `modelo` varchar(50) NOT NULL,
  `especificaciones` longtext DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_registro` date NOT NULL,
  `ubicacion` varchar(100) NOT NULL,
  `descripcion_larga` longtext DEFAULT NULL,
  `es_html` tinyint(1) NOT NULL,
  `valoracion_promedio` double NOT NULL,
  `cantidad_disponible` int(10) UNSIGNED NOT NULL CHECK (`cantidad_disponible` >= 0),
  `cantidad_total` int(10) UNSIGNED NOT NULL CHECK (`cantidad_total` >= 0),
  `precio_anio` decimal(10,2) DEFAULT NULL,
  `precio_dia` decimal(10,2) NOT NULL,
  `precio_mes` decimal(10,2) DEFAULT NULL,
  `precio_semana` decimal(10,2) DEFAULT NULL,
  `precio_semestre` decimal(10,2) DEFAULT NULL,
  `precio_trimestre` decimal(10,2) DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla `alquiler_equipo`
--

INSERT INTO `alquiler_equipo` (`id`, `marca`, `modelo`, `especificaciones`, `estado`, `fecha_registro`, `ubicacion`, `descripcion_larga`, `es_html`, `valoracion_promedio`, `cantidad_disponible`, `cantidad_total`, `precio_anio`, `precio_dia`, `precio_mes`, `precio_semana`, `precio_semestre`, `precio_trimestre`) VALUES
(1, 'a', 'a', 'a', 'alquilado', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(2, 'HP', 'a', 'a', 'alquilado', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(3, 'HP', 'a', 'a', 'disponible', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(4, 'HP', 'a', 'a', 'disponible', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(6, 'HP', 'a', 'a', 'mantenimiento', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(7, 'HP', 'a', 'a', 'mantenimiento', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(8, 'HP', 'a', 'a', 'disponible', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(9, 'HP', 'a', 'a', 'reservado', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(10, 'HP', 'a', 'a', 'reservado', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(11, 'HP', 'a', 'a', 'disponible', '2025-05-15', 'a', NULL, 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(12, 'HP', '1202', '13251251325', 'disponible', '2025-05-17', 'a', '156415', 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(13, 'fdfdf', 'dfdfdfd', 'ddfdf', 'alquilado', '2025-05-17', 'dfdfdfdfdf', 'ffdf', 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(14, 'HP00.0.0.0.0.0.', 'aaaaa543120.', '25402', 'disponible', '2025-05-19', '54120', '05050', 1, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(15, 'HP00.0.0.0.0.0.', 'aaaaa543120.', '25402', 'disponible', '2025-05-19', '54120', '05050', 1, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(18, '435543', 'adcscc', 'asasasa', 'alquilado', '2025-05-19', 'asa', 'sasasas', 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(19, '435543', 'adcscc', 'asasasa', 'alquilado', '2025-05-19', 'asa', 'sasasas', 0, 0, 1, 1, NULL, 0.00, NULL, NULL, NULL, NULL),
(21, '222222222222222aaaa', 'a', 'jabes', 'alquilado', '2025-05-20', 'Barranquilla', 'hnjnujyj', 1, 0, 12, 30, 2372500.00, 10000.00, 240000.00, 63000.00, 1260000.00, 675000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_fotoequipo`
--

CREATE TABLE `alquiler_fotoequipo` (
  `id` bigint(20) NOT NULL,
  `foto` varchar(100) NOT NULL,
  `es_principal` tinyint(1) NOT NULL,
  `fecha_subida` datetime(6) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `equipo_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_fotoequipo`
--

INSERT INTO `alquiler_fotoequipo` (`id`, `foto`, `es_principal`, `fecha_subida`, `descripcion`, `equipo_id`) VALUES
(3, 'equipos/asdsfv1010000/images_1.jpeg', 1, '2025-05-19 18:21:54.379053', 'Foto del equipo 435543 adcscc', 18),
(4, 'equipos/asdsfv101000010/imagen_2025-03-19_094249748.png', 1, '2025-05-19 18:23:08.270543', 'Foto del equipo 435543 adcscc', 19),
(6, 'equipos/34531010100/images_2.jpeg', 1, '2025-05-20 19:40:03.774819', 'Foto del equipo 222222222222222\' a', 21),
(7, 'equipos/34531010100/tecnonacho.jpg', 0, '2025-05-20 19:40:03.789883', 'Foto del equipo 222222222222222\' a', 21),
(8, 'equipos/34531010100/images_1.jpeg', 0, '2025-05-20 19:40:03.809654', 'Foto del equipo 222222222222222\' a', 21),
(9, 'equipos/34531010100/Imagen_de_WhatsApp_2025-04-23_a_las_11.13.59_fd7c0f51.jpg', 0, '2025-05-20 19:40:03.821767', 'Foto del equipo 222222222222222\' a', 21);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_pago`
--

CREATE TABLE `alquiler_pago` (
  `id` bigint(20) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha_pago` date NOT NULL,
  `metodo_pago` varchar(20) NOT NULL,
  `estado_pago` varchar(20) NOT NULL,
  `factura_generada` tinyint(1) NOT NULL,
  `referencia_transaccion` varchar(100) DEFAULT NULL,
  `alquiler_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_pago`
--

INSERT INTO `alquiler_pago` (`id`, `monto`, `fecha_pago`, `metodo_pago`, `estado_pago`, `factura_generada`, `referencia_transaccion`, `alquiler_id`) VALUES
(1, 100000.00, '2025-05-19', 'tarjeta', 'parcial', 0, '2023', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_rol`
--

CREATE TABLE `alquiler_rol` (
  `id` bigint(20) NOT NULL,
  `nombre_rol` varchar(50) NOT NULL,
  `descripcion` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_rol`
--

INSERT INTO `alquiler_rol` (`id`, `nombre_rol`, `descripcion`) VALUES
(1, 'cliente', ''),
(2, 'administrador', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_serialequipo`
--

CREATE TABLE `alquiler_serialequipo` (
  `id` bigint(20) NOT NULL,
  `numero_serie` varchar(100) NOT NULL,
  `equipo_id` bigint(20) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `fecha_registro` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_usuario`
--

CREATE TABLE `alquiler_usuario` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `nombre_usuario` varchar(100) NOT NULL,
  `estado_usuario` varchar(20) NOT NULL,
  `ultimo_acceso` datetime(6) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `cliente_id` bigint(20) DEFAULT NULL,
  `rol_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `alquiler_usuario`
--

INSERT INTO `alquiler_usuario` (`id`, `password`, `last_login`, `is_superuser`, `nombre_usuario`, `estado_usuario`, `ultimo_acceso`, `is_active`, `is_staff`, `cliente_id`, `rol_id`) VALUES
(1, 'pbkdf2_sha256$870000$nfoXIE1wFCa7hlNHaBJ6mb$yYbCc06rHcce+KVKwmu2zzITm4+j9C/5/O8vOFjKeDc=', '2025-03-25 16:52:47.748174', 0, 'Jabes', 'activo', '2025-03-25 16:52:43.170583', 1, 0, NULL, 1),
(2, 'pbkdf2_sha256$870000$u38FquTP82nVIp7CyofocL$pssN/GJOQDmV8/owFA6MPA7AfedkAeL8ckIFBHFUG5Y=', NULL, 1, 'Jabesinho', 'activo', '2025-03-25 17:36:30.987968', 1, 1, NULL, 2),
(3, 'pbkdf2_sha256$870000$FHWgpqo0oXS4yPp7rp4V2y$JAuESjSuF8pfARDqAoV3w1zuvmEq8MSMC/bNEhoum3g=', '2025-05-13 17:22:20.759521', 0, 'Jabezinho', 'activo', '2025-05-13 16:02:08.762234', 1, 0, 1, 1),
(4, 'pbkdf2_sha256$870000$ZG4Eq6cPgsKr2WETiBI0aR$MLCtAuCbLDSMkeFRG4LtqxbS3TEfkfC3SkF4NKPd3j8=', '2025-05-14 20:26:51.733255', 1, 'Jabesinhoo', 'activo', '2025-05-14 20:25:33.034813', 1, 1, NULL, 2),
(5, 'pbkdf2_sha256$870000$1qMGfFjo13gjZS3u3GO8Ua$T5MvY0ljSixCWSxsUOP+2xX+i3zTbk8GS+TnihE1GTo=', '2025-05-14 21:11:07.400818', 0, 'Jabezinhop', 'activo', '2025-05-14 21:11:07.388140', 1, 0, NULL, 1),
(6, 'pbkdf2_sha256$870000$dsRF3AwO8wForuXgkoPPyv$/7Puh2ZYQ25Oylx335eqPSgVUrpJHhrk7Luu78BZVjg=', '2025-05-24 16:08:27.618903', 0, 'Jabesinhooo', 'activo', '2025-05-14 21:26:45.685157', 1, 1, NULL, 1),
(7, 'pbkdf2_sha256$870000$XRqZlve6Dvf5fw017QP9ju$knZLSLQDgv8hJTiQYYk9q33ZtKS5o5c5GTlvNVT5q20=', '2025-05-15 16:06:14.557824', 0, 'marie', 'activo', '2025-05-15 16:06:14.524931', 1, 0, NULL, 1),
(8, 'pbkdf2_sha256$870000$CZ5n343gFIsultaQmQIHwL$e7t585JgH+mVCsjL5rmkfmVnu7d85PV1iY3/xLhveGw=', '2025-05-15 16:07:28.214987', 0, 'Maryee', 'activo', '2025-05-15 16:07:28.202140', 1, 0, NULL, 1),
(9, 'pbkdf2_sha256$870000$rsFCMUR3h7WezCpt2qf6uo$GqEB5kAFn/yYn0fiXX0Ak/x0Y/RtimPqETF1PjZkk68=', '2025-05-15 16:16:06.087575', 0, 'Richie', 'activo', '2025-05-15 16:15:59.000709', 1, 0, NULL, 1),
(10, 'pbkdf2_sha256$870000$J7M3pg3hFmQxzq3pdWKhUP$XR/yqeBJ5SpcDL2i1sNuIuWJYc1GvRBqcxBXso2iw1A=', '2025-05-15 19:46:52.479131', 1, 'karmye', 'activo', '2025-05-15 19:45:59.173127', 1, 1, NULL, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_usuario_groups`
--

CREATE TABLE `alquiler_usuario_groups` (
  `id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alquiler_usuario_user_permissions`
--

CREATE TABLE `alquiler_usuario_user_permissions` (
  `id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add cliente', 6, 'add_cliente'),
(22, 'Can change cliente', 6, 'change_cliente'),
(23, 'Can delete cliente', 6, 'delete_cliente'),
(24, 'Can view cliente', 6, 'view_cliente'),
(25, 'Can add equipo', 7, 'add_equipo'),
(26, 'Can change equipo', 7, 'change_equipo'),
(27, 'Can delete equipo', 7, 'delete_equipo'),
(28, 'Can view equipo', 7, 'view_equipo'),
(29, 'Can add rol', 8, 'add_rol'),
(30, 'Can change rol', 8, 'change_rol'),
(31, 'Can delete rol', 8, 'delete_rol'),
(32, 'Can view rol', 8, 'view_rol'),
(33, 'Can add alquiler', 9, 'add_alquiler'),
(34, 'Can change alquiler', 9, 'change_alquiler'),
(35, 'Can delete alquiler', 9, 'delete_alquiler'),
(36, 'Can view alquiler', 9, 'view_alquiler'),
(37, 'Can add contrato', 10, 'add_contrato'),
(38, 'Can change contrato', 10, 'change_contrato'),
(39, 'Can delete contrato', 10, 'delete_contrato'),
(40, 'Can view contrato', 10, 'view_contrato'),
(41, 'Can add pago', 11, 'add_pago'),
(42, 'Can change pago', 11, 'change_pago'),
(43, 'Can delete pago', 11, 'delete_pago'),
(44, 'Can view pago', 11, 'view_pago'),
(45, 'Can add usuario', 12, 'add_usuario'),
(46, 'Can change usuario', 12, 'change_usuario'),
(47, 'Can delete usuario', 12, 'delete_usuario'),
(48, 'Can view usuario', 12, 'view_usuario'),
(49, 'Can add notificacion', 13, 'add_notificacion'),
(50, 'Can change notificacion', 13, 'change_notificacion'),
(51, 'Can delete notificacion', 13, 'delete_notificacion'),
(52, 'Can view notificacion', 13, 'view_notificacion'),
(53, 'Can add orden compra', 14, 'add_ordencompra'),
(54, 'Can change orden compra', 14, 'change_ordencompra'),
(55, 'Can delete orden compra', 14, 'delete_ordencompra'),
(56, 'Can view orden compra', 14, 'view_ordencompra'),
(57, 'Can add item orden compra', 15, 'add_itemordencompra'),
(58, 'Can change item orden compra', 15, 'change_itemordencompra'),
(59, 'Can delete item orden compra', 15, 'delete_itemordencompra'),
(60, 'Can view item orden compra', 15, 'view_itemordencompra'),
(61, 'Can add Foto de equipo', 16, 'add_fotoequipo'),
(62, 'Can change Foto de equipo', 16, 'change_fotoequipo'),
(63, 'Can delete Foto de equipo', 16, 'delete_fotoequipo'),
(64, 'Can view Foto de equipo', 16, 'view_fotoequipo'),
(65, 'Can add Número de serie', 17, 'add_numeroserie'),
(66, 'Can change Número de serie', 17, 'change_numeroserie'),
(67, 'Can delete Número de serie', 17, 'delete_numeroserie'),
(68, 'Can view Número de serie', 17, 'view_numeroserie'),
(69, 'Can add serial equipo', 18, 'add_serialequipo'),
(70, 'Can change serial equipo', 18, 'change_serialequipo'),
(71, 'Can delete serial equipo', 18, 'delete_serialequipo'),
(72, 'Can view serial equipo', 18, 'view_serialequipo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(9, 'alquiler', 'alquiler'),
(6, 'alquiler', 'cliente'),
(10, 'alquiler', 'contrato'),
(7, 'alquiler', 'equipo'),
(16, 'alquiler', 'fotoequipo'),
(15, 'alquiler', 'itemordencompra'),
(13, 'alquiler', 'notificacion'),
(17, 'alquiler', 'numeroserie'),
(14, 'alquiler', 'ordencompra'),
(11, 'alquiler', 'pago'),
(8, 'alquiler', 'rol'),
(18, 'alquiler', 'serialequipo'),
(12, 'alquiler', 'usuario'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-03-25 16:24:23.252699'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-03-25 16:24:23.418202'),
(3, 'auth', '0001_initial', '2025-03-25 16:24:23.986284'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-03-25 16:24:24.086419'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-03-25 16:24:24.094619'),
(6, 'auth', '0004_alter_user_username_opts', '2025-03-25 16:24:24.103084'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-03-25 16:24:24.112272'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-03-25 16:24:24.116754'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-03-25 16:24:24.125900'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-03-25 16:24:24.133308'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-03-25 16:24:24.141652'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-03-25 16:24:24.200984'),
(13, 'auth', '0011_update_proxy_permissions', '2025-03-25 16:24:24.210784'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-03-25 16:24:24.218504'),
(15, 'alquiler', '0001_initial', '2025-03-25 16:24:25.744804'),
(16, 'admin', '0001_initial', '2025-03-25 16:24:25.973034'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-03-25 16:24:25.988245'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-03-25 16:24:26.001601'),
(19, 'sessions', '0001_initial', '2025-03-25 16:24:26.099349'),
(20, 'alquiler', '0002_alter_usuario_rol_notificacion', '2025-03-25 17:23:54.666251'),
(21, 'alquiler', '0003_ordencompra_itemordencompra', '2025-03-25 19:45:35.858431'),
(22, 'alquiler', '0004_remove_notificacion_cliente_delete_itemordencompra_and_more', '2025-03-25 21:28:08.414297'),
(23, 'alquiler', '0005_alter_usuario_rol', '2025-05-13 18:04:32.428125'),
(24, 'alquiler', '0006_alter_usuario_rol', '2025-05-13 19:48:32.338004'),
(25, 'alquiler', '0007_fotoequipo_alter_equipo_options_and_more', '2025-05-16 16:04:08.061595'),
(26, 'alquiler', '0008_equipo_cantidad_disponible_equipo_cantidad_total_and_more', '2025-05-20 18:29:01.022943'),
(27, 'alquiler', '0009_alter_alquiler_cliente', '2025-05-23 18:02:56.128956'),
(28, 'alquiler', '0010_alter_alquiler_precio_total', '2025-05-24 20:18:24.517302'),
(29, 'alquiler', '0011_cliente_barrio_cliente_ciudad_and_more', '2025-05-26 16:52:49.764268'),
(30, 'alquiler', '0012_alter_cliente_tipo_cliente', '2025-05-26 16:54:34.230007'),
(31, 'alquiler', '0013_alquiler_fecha_creacion_alquiler_numero_factura', '2025-05-26 21:14:17.063599'),
(32, 'alquiler', '0014_numeroserie', '2025-05-27 14:47:13.512013'),
(33, 'alquiler', '0015_remove_equipo_numero_serie_serialequipo_and_more', '2025-05-27 15:07:05.157070'),
(34, 'alquiler', '0016_alter_serialequipo_options_serialequipo_activo_and_more', '2025-05-27 17:35:13.299040'),
(35, 'alquiler', '0017_alter_serialequipo_fecha_registro', '2025-05-27 17:46:29.859864');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('1o2phna070i60iue0tt3gq7giwjxjlj0', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uI71m:pP2nMLNAMSIM0RDcz2Sz2bwMUGCkeqr3zRvgz4PYlI0', '2025-06-05 14:36:10.460580'),
('2abgkuyxeime2esvnm381mqrub0r55e9', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uH1VD:Ib5UgX5a8WSwGCw7WHWDlCyWEt3R-o1sKHjJmnT1B9c', '2025-06-02 14:30:03.955855'),
('3mfkgoo91g3gimmxf0wburb58bj63k4d', 'e30:1uEt17:gyWhPX7_cvMZP7xFupWPNnPhlpQIQ87XW2L3qhHpXyM', '2025-05-27 17:02:09.129699'),
('5uz8nxt60ni55fwgl75b0kzondc88e7a', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uH1ot:vKkjjCPqAmMER_3bBIjghacSOwc1ydjYV6t_zqhSJpg', '2025-06-02 14:50:23.349025'),
('6pzq25aukas80ctq5isw1hevfr21ebpi', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uI6Fp:ig8WCF1029JAtV-6g54M5LEp6-EuzUw8TgWtwHS4iK4', '2025-06-05 13:46:37.025554'),
('8bkfarubnmxjvb01ryntzbhna57t8ufz', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uH3fP:60bubegf1jKyh-65j6O62V7WaXn1rOOTsh3d6wSBCEw', '2025-06-02 16:48:43.702019'),
('8daaparw00lzzbkylcn8edu49oxsouxe', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uIrQB:RxgolToEaLRnrymlP0aljsLQH1LrUXxhLyOnzqA6I5g', '2025-06-07 16:08:27.624202'),
('8vls98ta53ce33w7t3mckem0wduqz1j6', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uI8sg:JVK7JOCm8M8O6GwkfBzQ4Bqoyz3X0-YYP3hrjbrip_k', '2025-06-05 16:34:54.584636'),
('9c3fb69qbwmzgyxx1srnwcirmlbxh6w4', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uIZnZ:XT29TnjubJXP9hhHFzkn6Uu_BgpcCR6_s-6bWS7KAT8', '2025-06-06 21:19:25.782184'),
('ch71501cfisce7sell35e71efnmhwknx', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uITNB:qM-Dvk1wJ4ET1MtPQU8W0PuDxVI0KQk0Hgjk69ChMfs', '2025-06-06 14:27:45.673559'),
('ckuev4wtpnx9sgnscjlnegkg313crb05', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uH2vQ:exgypPU5Nz37_kE8zxmXJ9xkPIvxvJgGJrWAqJXlXCU', '2025-06-02 16:01:12.517086'),
('ha3c5bbl5mtgppcvsdbj7f6hplu6sbgm', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uIZjs:lrUgwpvmzch9zIFLVIMh8ZoBL14CBfFF7egtTS2IyL4', '2025-06-06 21:15:36.073932'),
('hgsdvp94zp7bjuuhpw9hj3opqzcgk9g6', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uH1aX:WX9CMajoVG9jyoAg-K68_SgkQaHgvh7rL_sNOR7RkLI', '2025-06-02 14:35:33.679349'),
('hjrocjw94ydmmk6nhob8okslz7zwrh1q', 'e30:1uFIgl:1OqrAU3vWrE_jdU0wHn36-GVU8dgBHUyh8DHuJxkDYA', '2025-05-28 20:26:51.724770'),
('hyprq8j1r5bum7nedas60n9ad97xaffu', 'e30:1uFIfq:AoURY-4zaitKF8Yq47ybSUpyYJlqBVhq7eu5ZIhOBFg', '2025-05-28 20:25:54.528910'),
('lp3bcqxuzfxy3hjbyy7yua73h85isxjc', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uIDfu:_mny6pONydAIcXmq5kL1wEO4Jy8mQSFFH38u0dFsIQc', '2025-06-05 21:42:02.117503'),
('mror5pfer3oy9w9h9u95nbg91veygro1', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uH1Jf:zJONYXRjENk-wc1jn_qsKv7XhnLpKtjOqx2cPg_c5j0', '2025-05-19 14:23:07.728540'),
('o3r87vh8b8zc3li5v5tzkxbi299seccm', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uIqiO:OREXcYmQ_z03F9kMQO_etv2ODTaKXPE1qQjtup_cFtc', '2025-06-07 15:23:12.068005'),
('p65mvpka9di132g4sgiuyp9rivvb2c86', 'e30:1uH1Ib:usP5ldOKkaF_Nil6DNphg8Ny2NrbteYTSGoiv21OmsI', '2025-05-19 14:22:01.041721'),
('qlfjvybjjvw7svluwdp1dkqi0tlaxmf4', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uG18t:nAVwtmsDn6oUEoGuCGbEBNhC6yTpexnAyRyJkHwfKro', '2025-05-30 19:54:51.805665'),
('r0b2gj5lxcqrckjh66o9hcvmx9r74te8', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uIALK:iQhPKl72_-1yCJh6kgeTfBl0U42qmfELE-M_m3LPNc4', '2025-06-05 18:08:34.613034'),
('tzthl2ragxsh2nclrhtlb5ethttlidbi', 'e30:1uEtKe:tC3fGRXThXM8SCAz2M0P2rbebdCtdkS0gs_4phSvp4M', '2025-05-27 17:22:20.749247'),
('uru7nbd7jzckf5we3eozugfxfsyy3otr', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uHRHU:BDvxPflvu7uL27HqRlNYy83m5L_pMG3oPlx4allwYOc', '2025-06-03 18:01:36.952746'),
('wxocuc1ig7ttc44fx87yi5foxr66qr5p', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uFwuc:HzM1EMGQJhGO0vwM7bVpRazAISMDeIjluaW7l6DXgp0', '2025-05-30 15:23:50.080063'),
('y9hw50wvtp9vnh4jfpkp7ik2djgxknv7', '.eJxVjMsOwiAQRf-FtSGDvF269xvIAINUDSSlXRn_3TbpQrf3nHPfLOC61LAOmsOU2YUZdvrdIqYntR3kB7Z756m3ZZ4i3xV-0MFvPdPrerh_BxVH3epzArC2GDA2gzcoJESFsoBCJKN9FMorkgCaKGobwTkqfjOc8DJryT5fxQ43DQ:1uI854:6WnJWXp-ZarU1hDWKD4AaEsbtcRDwq6EBcO37KZfXvw', '2025-06-05 15:43:38.778598'),
('z6j1zcrcw3iluo1eq6mhowekp5mf9c1l', 'e30:1uFJm5:hkkjZmUQtuh-A5U9Dhvjw87EYnjvicf6xKAXNSQnDN0', '2025-05-28 21:36:25.066821');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alquiler_alquiler`
--
ALTER TABLE `alquiler_alquiler`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`),
  ADD KEY `alquiler_alquiler_cliente_id_625dcd53_fk_alquiler_cliente_id` (`cliente_id`),
  ADD KEY `alquiler_alquiler_equipo_id_e212d306_fk_alquiler_equipo_id` (`equipo_id`);

--
-- Indices de la tabla `alquiler_cliente`
--
ALTER TABLE `alquiler_cliente`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `alquiler_contrato`
--
ALTER TABLE `alquiler_contrato`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `alquiler_id` (`alquiler_id`);

--
-- Indices de la tabla `alquiler_equipo`
--
ALTER TABLE `alquiler_equipo`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `alquiler_fotoequipo`
--
ALTER TABLE `alquiler_fotoequipo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `alquiler_fotoequipo_equipo_id_6ddf7d02_fk_alquiler_equipo_id` (`equipo_id`);

--
-- Indices de la tabla `alquiler_pago`
--
ALTER TABLE `alquiler_pago`
  ADD PRIMARY KEY (`id`),
  ADD KEY `alquiler_pago_alquiler_id_3d8ae7ab_fk_alquiler_alquiler_id` (`alquiler_id`);

--
-- Indices de la tabla `alquiler_rol`
--
ALTER TABLE `alquiler_rol`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre_rol` (`nombre_rol`);

--
-- Indices de la tabla `alquiler_serialequipo`
--
ALTER TABLE `alquiler_serialequipo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_serie` (`numero_serie`),
  ADD KEY `alquiler_serialequipo_equipo_id_2e183fd0_fk_alquiler_equipo_id` (`equipo_id`);

--
-- Indices de la tabla `alquiler_usuario`
--
ALTER TABLE `alquiler_usuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  ADD UNIQUE KEY `cliente_id` (`cliente_id`),
  ADD KEY `alquiler_usuario_rol_id_f70ed025_fk_alquiler_rol_id` (`rol_id`);

--
-- Indices de la tabla `alquiler_usuario_groups`
--
ALTER TABLE `alquiler_usuario_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `alquiler_usuario_groups_usuario_id_group_id_7ccfd68d_uniq` (`usuario_id`,`group_id`),
  ADD KEY `alquiler_usuario_groups_group_id_2d220838_fk_auth_group_id` (`group_id`);

--
-- Indices de la tabla `alquiler_usuario_user_permissions`
--
ALTER TABLE `alquiler_usuario_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `alquiler_usuario_user_pe_usuario_id_permission_id_fa83791b_uniq` (`usuario_id`,`permission_id`),
  ADD KEY `alquiler_usuario_use_permission_id_0c432404_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indices de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indices de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indices de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_alquiler_usuario_id` (`user_id`);

--
-- Indices de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indices de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `alquiler_alquiler`
--
ALTER TABLE `alquiler_alquiler`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `alquiler_cliente`
--
ALTER TABLE `alquiler_cliente`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `alquiler_contrato`
--
ALTER TABLE `alquiler_contrato`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `alquiler_equipo`
--
ALTER TABLE `alquiler_equipo`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `alquiler_fotoequipo`
--
ALTER TABLE `alquiler_fotoequipo`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de la tabla `alquiler_pago`
--
ALTER TABLE `alquiler_pago`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `alquiler_rol`
--
ALTER TABLE `alquiler_rol`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `alquiler_serialequipo`
--
ALTER TABLE `alquiler_serialequipo`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `alquiler_usuario`
--
ALTER TABLE `alquiler_usuario`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `alquiler_usuario_groups`
--
ALTER TABLE `alquiler_usuario_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `alquiler_usuario_user_permissions`
--
ALTER TABLE `alquiler_usuario_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=73;

--
-- AUTO_INCREMENT de la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alquiler_alquiler`
--
ALTER TABLE `alquiler_alquiler`
  ADD CONSTRAINT `alquiler_alquiler_cliente_id_625dcd53_fk_alquiler_cliente_id` FOREIGN KEY (`cliente_id`) REFERENCES `alquiler_cliente` (`id`),
  ADD CONSTRAINT `alquiler_alquiler_equipo_id_e212d306_fk_alquiler_equipo_id` FOREIGN KEY (`equipo_id`) REFERENCES `alquiler_equipo` (`id`);

--
-- Filtros para la tabla `alquiler_contrato`
--
ALTER TABLE `alquiler_contrato`
  ADD CONSTRAINT `alquiler_contrato_alquiler_id_d3e98942_fk_alquiler_alquiler_id` FOREIGN KEY (`alquiler_id`) REFERENCES `alquiler_alquiler` (`id`);

--
-- Filtros para la tabla `alquiler_fotoequipo`
--
ALTER TABLE `alquiler_fotoequipo`
  ADD CONSTRAINT `alquiler_fotoequipo_equipo_id_6ddf7d02_fk_alquiler_equipo_id` FOREIGN KEY (`equipo_id`) REFERENCES `alquiler_equipo` (`id`);

--
-- Filtros para la tabla `alquiler_pago`
--
ALTER TABLE `alquiler_pago`
  ADD CONSTRAINT `alquiler_pago_alquiler_id_3d8ae7ab_fk_alquiler_alquiler_id` FOREIGN KEY (`alquiler_id`) REFERENCES `alquiler_alquiler` (`id`);

--
-- Filtros para la tabla `alquiler_serialequipo`
--
ALTER TABLE `alquiler_serialequipo`
  ADD CONSTRAINT `alquiler_serialequipo_equipo_id_2e183fd0_fk_alquiler_equipo_id` FOREIGN KEY (`equipo_id`) REFERENCES `alquiler_equipo` (`id`);

--
-- Filtros para la tabla `alquiler_usuario`
--
ALTER TABLE `alquiler_usuario`
  ADD CONSTRAINT `alquiler_usuario_cliente_id_05320ea2_fk_alquiler_cliente_id` FOREIGN KEY (`cliente_id`) REFERENCES `alquiler_cliente` (`id`),
  ADD CONSTRAINT `alquiler_usuario_rol_id_f70ed025_fk_alquiler_rol_id` FOREIGN KEY (`rol_id`) REFERENCES `alquiler_rol` (`id`);

--
-- Filtros para la tabla `alquiler_usuario_groups`
--
ALTER TABLE `alquiler_usuario_groups`
  ADD CONSTRAINT `alquiler_usuario_gro_usuario_id_224b948c_fk_alquiler_` FOREIGN KEY (`usuario_id`) REFERENCES `alquiler_usuario` (`id`),
  ADD CONSTRAINT `alquiler_usuario_groups_group_id_2d220838_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `alquiler_usuario_user_permissions`
--
ALTER TABLE `alquiler_usuario_user_permissions`
  ADD CONSTRAINT `alquiler_usuario_use_permission_id_0c432404_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `alquiler_usuario_use_usuario_id_80ef422a_fk_alquiler_` FOREIGN KEY (`usuario_id`) REFERENCES `alquiler_usuario` (`id`);

--
-- Filtros para la tabla `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Filtros para la tabla `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Filtros para la tabla `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_alquiler_usuario_id` FOREIGN KEY (`user_id`) REFERENCES `alquiler_usuario` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
