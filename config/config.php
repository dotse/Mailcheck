<?php

abstract class Config
{
	private static $data = array(
		// Site version number
		'MAILCHECK_VERSION'			=> 'MailCheck Beta 7-20120220',
		// Version number appended to scripts files
		'SCRIPT_VERSION'			=> 5,

		// Number of old test per page in the history part
		'HISTORY_PAGE_SIZE'			=> 10,
		
		'database' => array(
			'host' => 'localhost',
			'database' => 'mailcheck',
			'username' => '<ENTER USERNAME HERE>',
			'password' => '<ENTER PASSWORD HERE>',
			),

		'testLimits' => array(
			// Cooldown period before we can run tests against the same domain again
			'cooldown' => 60, // seconds
			),

		// IP based frequency settings
		'clientIpLimit' => array(
			'frequency' => 86400, // seconds 
			'max_tests' => 20,
			),

		// Addresses users should send emails to for some tests
		'emailAddresses' => 'mcsmtp25@mailcheck.iis.se,mcsmtp25@gmail.com,mcsmtp25@hotmail.com',
		'outlookEmailAddresses' => 'mcsmtp25@mailcheck.iis.se;mcsmtp25@gmail.com;mcsmtp25@hotmail.com',
		'bugreportEmail' => '<ENTER EMAIL HERE>',

	);
	
	public static function get($p1, $p2 = null)
	{
		if ($p2 === null)
			return self::$data[$p1];
		else
			return self::$data[$p1][$p2];
	}
}
