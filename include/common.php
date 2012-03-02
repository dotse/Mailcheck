<?php

session_start();

require_once dirname(__FILE__) . '/../config/config.php';
require_once dirname(__FILE__) . '/database.php';
require_once dirname(__FILE__) . '/template.php';
require_once dirname(__FILE__) . '/requests.php';

// Setup locale settings for gettext translation
$locale = getLanguage();
$domain = 'mailcheck';

setlocale(LC_ALL, "$locale.utf8");
bindtextdomain($domain, dirname(__FILE__).'/../locale');
textdomain($domain);
bind_textdomain_codeset($domain, 'UTF-8');


/**
 * Translate a string
 *
 * @param string $text		String key in translation files
 * @param array $params		(Optional) Parameters used in the translation text
 */
function translate($text, $params = null)
{
	if ($text == '')
		return $text;

	$t = gettext($text);
	if ($params != null)
	{
		$strParams = array();
		$t = vsprintf($t, $params);
	}

	return $t;
}


function sanitize_hash($hash)
{
	return preg_replace("/[^0-9a-fA-F]/", "", $hash);
}


function statusToClass($status)
{
//	if ($status == 0)
//		return 'unknown';
	if ($status == 1)
		return 'ok';
	else if ($status == 2)
		return 'warn';
	else if ($status == 3)
		return 'error';
	else if ($status == 4)
		return 'unkown';
	return '';
}

function autoFormatSeconds($seconds)
{
	$data = array();
	$data['days'] = intval($seconds / 86400);
	$ssLeft = $seconds - ($data['days']*86400);
	$data['hours'] = intval($ssLeft / 3600);
	$ssLeft = $ssLeft - ($data['hours'] * 3600);
	$data['minutes'] = intval($ssLeft / 60);
	$data['seconds'] = $ssLeft - ($data['minutes'] * 60);

	if ($data['days'] > 0)
		$ret = array('days', $data['days']);
	else if ($data['hours'] > 0)
		$ret = array('hours', $data['hours']);
	else if ($data['minutes'] > 0)
		$ret = array('minutes', $data['minutes']);
	else
		$ret = array('seconds', $data['seconds']);
	if ($ret[1] == 1)
		$ret[0] = substr($ret[0], 0, -1);
	return $ret;
}

function formatSeconds($seconds, $format)
{
	$formats = array('d' => 86400, 'h' => 3600, 'm' => 60);
	if ($format == 's')
		return $seconds;

	$unit = 0;
	while ($seconds > 0)
	{
		$unit++;
		$seconds -= $formats[$format];
	}
	return $unit;
}

/**
 *
 */
function createTestResultUrl($testId, $time=null)
{
	$baseUrl = 'http://' . $_SERVER['SERVER_NAME'] . '/result/';
	if (is_numeric($testId))
		return $baseUrl . $time . '-' . $testId;

	return $baseUrl . $testId;
}

function unitToSeconds($unit)
{
	$time = array(
		'seconds' => 0,
		'hours' => 60 * 60,
		'days' => 60 * 60 * 24,
		'weeks' => 60 * 60 * 24 * 7,
		'months' => 60 * 60 * 24 * 7 * 4.3
		);
		
	if (array_key_exists($unit, $time))
		return $time[$unit];
	return 0;
}

function getLanguage()
{
	$lang = 'en_US'; // Defulat language

	if (isset($_SESSION['lang']) && in_array($_SESSION['lang'], array('sv_SE', 'en_US')))
	{
		$lang = $_SESSION['lang'];
	}

	return $lang;
}

function setLanguage($lang)
{
	$_SESSION['lang'] = $lang;
}

function filter_lang($lang)
{
	if (in_array($lang, array('en_US', 'sv_SE')) == false)
		return 'sv_SE';
	return $lang;
}
