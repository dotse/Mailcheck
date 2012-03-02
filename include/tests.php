<?php

require_once dirname(__FILE__) . '/../include/database.php';

/**
 * Are we allowed to start a test against a domain?
 *
 * @param string $domain
 * @return bool
 */
function isAllowedToStart($domain)
{
	$customMessage = false; 
	$foundIPRule = false;
	$remoteIP = $_SERVER['REMOTE_ADDR'];
	
	// Check IP test frequency against special rules (how often a single IP is starting tests)
	$result = Database::query('SELECT id, ip, max_tests, interval FROM frequency_ip');
	foreach ($result as $r)
	{
		if ($r['ip'] == $remoteIP)
		{
			$foundIPRule = true;
			if (isFrequencyReached($r['max_tests'], $r['interval'], null, $r['ip']) == false)
			{
				$allowed = false;
				$time = autoFormatSeconds($r['interval']);
				if ($time[1] == 1)
					$message = translate('Your IP have started too many tests the last %s', array(translate($time[0])));
				else
					$message = translate('Your IP have started too many tests the last %s', array($time[1])) . ' '. translate($time[0]);
				return array($message, $customMessage);
			}
		}
	}

	// If no special rule existed for remote IP, we use the general rule
	if ($foundIPRule == false)
	{
		$maxTests = Config::get('clientIpLimit', 'max_tests');
		$time = Config::get('clientIpLimit', 'frequency');
		if (isFrequencyReached($maxTests, $time, null, $remoteIP) == false)
		{
				$time = autoFormatSeconds($r['interval']);
				if ($time[1] == 1)
					$message = translate('Your IP have started too many tests the last %s', array(translate($time[0])));
				else
					$message = translate('Your IP have started too many tests the last %s', array($time[1])) . ' '. translate($time[0]);
				return array($message, $customMessage);

		}
	}

	// Check lower start limit
	if (($lowerLimit = Config::get('testLimits', 'cooldown')) > 0)
	{
		// Make sure tests can't be started too often
		$result = Database::query("SELECT domain FROM test WHERE domain = ? AND started >= now() - interval '$lowerLimit seconds' LIMIT 1", array($domain));
		if (is_array($result) && count($result) > 0)
		{
			return array(translate('Too many tests started within the last %s seconds', formatSeconds($lowerLimit, 's')), $customMessage);
		}
	}

	// Check for specific frequency rule
	$result = Database::query('SELECT domain,max_tests,interval,description FROM frequency');
	if (is_array($result) != true) // we should always get at least the special rule *.
		return true;

	$message = '';
	$allowed = true;
	$matchFound = false;
	$specialRule = null;
	foreach ($result as $r)
	{
		if ($r['domain'] == '*')
		{
			$specialRule = $r;
			continue;
		}

		if (fnmatch($r['domain'], $domain))
		{
			$matchFound = true;
			if ($r['max_tests'] > 0 && $r['interval'] > 0)
			{	
				if (isFrequencyReached($r['max_tests'], $r['interval'], $domain) == false)
				{
					$allowed = false;
					$time = autoFormatSeconds($r['interval']);
					if ($time[1] == 1)
						$message = translate('Domain has been tested too many times the last %s', array(translate($time[0])));
					else
						$message = translate('Domain has been tested too many times the last %s', array($time[1])) . ' '. translate($time[0]);
				}
			}
			else // blacklisted
			{
				$allowed = false;
				$message = translate('You are not allowed to test this domain');
			}

			// Show the special description if we have one
			if ($r['description'] != '')
			{
				$customMessage = true;
				$message = $r['description'];
			}
		}
	}
	
	// If not specific rule was found, check against the common rule if it exists
	if ($specialRule !== null && $matchFound == false)
	{
		if (isFrequencyReached($specialRule['max_tests'], $specialRule['interval'], $domain) == false)
		{
			$allowed = false;
			$time = autoFormatSeconds($specialRule['interval']);
			if ($time[1] == 1)
			{
				$message = translate('Domain has been tested too many times the last %s', array(translate($time[0])));
			}
			else
			{
				$message = translate('Domain has been tested too many times the last %s', array($time[1])) . ' '. translate($time[0]);
			}
		}
	}

	if ($allowed !== true)
		return array($message, $customMessage);
	else
		return $allowed;
}

/**
 * Checks if the domain is able to run within the specified frequency interval.
 *
 * @param int $maxTests			Max tests within the interval
 * @param int $interval			Interval time in seconds
 * @param string $domain		The domain we are testing. If null, paramters $ip must be specified.
 * @param string $ip			(Optional) If specified, we are testing against IP instead of domain.
 * @return boolean				True if we are allow to the, else false.
 * @TODO:	Name does not logically work with the return value
 */
function isFrequencyReached($maxTests, $interval, $domain, $ip=null)
{
	$col = 'domain';
	$value = $domain;
	if ($domain == null)
	{
		$col = 'ip';
		$value = $ip;
	}

	$count = Database::query("SELECT count(id) FROM test WHERE $col = ? AND started > now() - interval '" . $interval. " seconds'", array($value));
	$count = $count[0]['count'];
	if ($count >= $maxTests)
		return false;
	return true;
}


?>
