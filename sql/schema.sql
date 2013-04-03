CREATE TABLE `articles` (
    `id` INTEGER NOT NULL PRIMARY KEY,
    `lastparsed` DATETIME NOT NULL,
    `title` VARCHAR(200) NOT NULL UNIQUE,
    `linkincount` INTEGER NOT NULL DEFAULT 0,
    `linkoutcount` INTEGER NOT NULL DEFAULT 0,
    INDEX USING HASH (`title`)
);

CREATE TABLE `links` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `article_id` INTEGER NOT NULL,
    `token_index` INTEGER NOT NULL,
    `target_article` VARCHAR(200) NOT NULL,
    FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`),
    INDEX (`article_id`)
);

CREATE TABLE `disambiguations` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `string` VARCHAR(200) NOT NULL,
    `meaning` VARCHAR(200) NOT NULL,
    `article_id` INTEGER NOT NULL,
    `token_index` INTEGER NOT NULL,
    FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`),
    INDEX (`article_id`),
    INDEX USING HASH (`string`)
);