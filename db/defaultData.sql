------------------
-- Default plugin settings
-----------------
INSERT INTO plugin_config ("key", value, "comment") VALUES ('connection_warning_length', '1', 'Time on seconds when a connection time is considered too long');
INSERT INTO plugin_config ("key", value, "comment") VALUES ('max_ssl_cert_age', '31536000', 'Maximum age for SSL cert');
INSERT INTO plugin_config ("key", value, "comment") VALUES ('min_ssl_cert_bits', '512', 'Minimum certificate bits for VerifyCert');

------------------
-- General test frequenct setting
------------------
INSERT INTO frequency ("domain", max_tests, "interval", description, created_email, created_ip) VALUES ('*', 5, 86400, '', NULL, NULL);

