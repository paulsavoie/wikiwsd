CREATE DATABASE `wikiwsd3` DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
GRANT ALL ON `wikiwsd3`.* TO `wikiwsd`@`localhost` IDENTIFIED BY 'wikiwsd';
GRANT ALL ON `wikiwsd3`.* TO `wikiwsd`@`%` IDENTIFIED BY 'wikiwsd';

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

-- VERSION 2 & 3
CREATE TABLE `redirects` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `source_article_name` VARCHAR(200) NOT NULL UNIQUE,
    `target_article_name` VARCHAR(200) NOT NULL,
    INDEX USING HASH (`source_article_name`)
);

CREATE TABLE `articles` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY,
    `lastparsed` DATETIME NOT NULL,
    `title` VARCHAR(200) NOT NULL UNIQUE,
    `articleincount` INTEGER NOT NULL DEFAULT 0,
    INDEX USING HASH (`title`)
);

CREATE TABLE `disambiguations` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `string` VARCHAR(200) NOT NULL,
    `target_article_id` BIGINT UNSIGNED NOT NULL,
    `occurrences` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (`target_article_id`) REFERENCES `articles` (`id`),
    INDEX USING HASH (`string`),
    INDEX (`target_article_id`)
);

CREATE TABLE `links` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `source_article_id` BIGINT UNSIGNED NOT NULL,
    `target_article_id` BIGINT UNSIGNED NOT NULL,
    `count` INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (`source_article_id`) REFERENCES `articles` (`id`),
    FOREIGN KEY (`target_article_id`) REFERENCES `articles` (`id`),
    INDEX (`target_article_id`),
    INDEX (`source_article_id`)
);

CREATE TABLE `ngrams` (
    `id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `string` VARCHAR(200) NOT NULL,
    `occurrences` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `as_link` BIGINT UNSIGNED NOT NULL DEFAULT 0
);

-- retrieve number of articles that link to A and B
SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM (SELECT source_article_id, target_article_id FROM article_links WHERE target_article_id=18948043 OR target_article_id=272207) AS tmp GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp2;

cur.execute('INSERT INTO article_links(source_article_id, target_article_id, count) VALUES(%s, %s, 1) ON DUPLICATE KEY UPDATE count=count+1;', (source_id, target_id))