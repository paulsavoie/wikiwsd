CREATE DATABASE `wikiwsd`;
GRANT ALL ON `wikiwsd`.* TO `wikiwsd`@`localhost` IDENTIFIED BY 'wikiwsd';
GRANT ALL ON `wikiwsd`.* TO `wikiwsd`@`%` IDENTIFIED BY 'wikiwsd';

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

CREATE TABLE `disambiguations_reduced` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    INDEX USING HASH (`string`)
    ) SELECT COUNT(*) AS `occurrences`, `string`, `meaning` FROM disambiguations GROUP BY `string`, `meaning`;

-- TODO

CREATE TABLE `links_reduced` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`),
    INDEX (`article_id`)
) SELECT COUNT(*) as `numlinks`, `article_id`, `target_article` FROM links GROUP BY `article_id`, `target_article`;

-- retrieve number of articles that link to A and B
SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM (SELECT source_article_id, target_article_id FROM article_links WHERE target_article_id=18948043 OR target_article_id=272207) AS tmp GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp2;