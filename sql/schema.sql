CREATE DATABASE `wikiwsd2`;
GRANT ALL ON `wikiwsd2`.* TO `wikiwsd`@`localhost` IDENTIFIED BY 'wikiwsd';
GRANT ALL ON `wikiwsd2`.* TO `wikiwsd`@`%` IDENTIFIED BY 'wikiwsd';

CREATE TABLE `articles` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY,
    `lastparsed` DATETIME NOT NULL,
    `title` VARCHAR(200) NOT NULL UNIQUE,
    `linkincount` INTEGER NOT NULL DEFAULT 0,
    `linkoutcount` INTEGER NOT NULL DEFAULT 0,
    INDEX USING HASH (`title`)
);

CREATE TABLE `links` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `article_id` BIGINT UNSIGNED NOT NULL,
    `token_index` INTEGER NOT NULL,
    `target_article` VARCHAR(200) NOT NULL,
    FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`),
    INDEX (`article_id`)
);

CREATE TABLE `disambiguations` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `string` VARCHAR(200) NOT NULL,
    `meaning` VARCHAR(200) NOT NULL,
    `article_id` BIGINT UNSIGNED NOT NULL,
    `token_index` INTEGER NOT NULL,
    FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`),
    INDEX (`article_id`),
    INDEX USING HASH (`string`)
);

CREATE TABLE `article_links` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `source_article_id` BIGINT UNSIGNED NOT NULL,
    `target_article_id` BIGINT UNSIGNED NOT NULL,
    `count` INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (`source_article_id`) REFERENCES `articles` (`id`),
    FOREIGN KEY (`target_article_id`) REFERENCES `articles` (`id`),
    INDEX (`target_article_id`)
);

CREATE TABLE `redirects` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `source_article_name` VARCHAR(200) NOT NULL,
    `target_article_name` VARCHAR(200) NOT NULL,
    INDEX USING HASH (`source_article_name`)
);

-- TODO

-- retrieve number of articles that link to A and B
SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM (SELECT source_article_id, target_article_id FROM article_links WHERE target_article_id=18948043 OR target_article_id=272207) AS tmp GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp2;

