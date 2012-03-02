<?php

/**
 * Provides filtering of input data.
 */
class Filter
{
	private $_filterTypes = array(
		'string' => FILTER_SANITIZE_STRING,
		'email' => FILTER_SANITIZE_EMAIL,
		'url' => FILTER_SANITIZE_URL,
		'int' => FILTER_SANITIZE_NUMBER_INT,
		'float' => FILTER_SANITIZE_NUMBER_FLOAT,
		'hash' => 'hash',
		);

	private static $instance = null;

	private function __construct()
	{ }

	public static function getInstance()
	{
		if (self::$instance == null)
			self::$instance = new Filter();
		return self::$instance;
	}

	/**
	 * Check if a fiter exists.
	 * @param string	Name of the filter
	 */
	public function hasFilter($type)
	{
		return isset($this->_filterType[$type]);
	}

	/**
	 * Filter input
	 * @param string $input		Input that is to be filtered.
	 * @param string $type		Filter that should be used.
	 * @return					Filtered string.
	 */
	public function filter($input, $type)
	{
		$filterType = $this->_filterTypes[$type];
		if (is_int($filterType))
			return filter_var($input, $filterType);
		else if ($filterType == 'hash')
		{
			return preg_replace("/[^0-9a-fA-F]/", "", $input);
		}
	}
}


class Validation
{
	private $_validatorTypes = array(
		'bool' => FILTER_VALIDATE_BOOLEAN,
		'email' => FILTER_VALIDATE_EMAIL,
		'url' => FILTER_VALIDATE_URL,
		'int' => FILTER_VALIDATE_INT,
		'float' => FILTER_VALIDATE_FLOAT,
		'ip' => FILTER_VALIDATE_IP,
		);

	private static $instance = null;

	private function __construct()
	{ }

	public static function getInstance()
	{
		if (self::$instance == null)
			self::$instance = new Validation();
		return self::$instance;
	}

	public function hasValidator($type)
	{
		return isset($this->_validatorTypes[$type]);
	}

	public function isValid($input, $type)
	{
		$validatorType = $this->_validatorTypes[$type];
		if (filter_var($input, $validatorType))
			return true;
		return false;
	}

	public static function validate($input, $type)
	{
		$v = Validation::getInstance();
		if ($v->hasValidator($type) == false)
			return false;
		
		return $v->isValid($input, $type);
	}
}

/**
 * Easy access GET and POST with filtering and validation.
 */
class Request
{
	public function __construct()
	{
	}

	public function POST($name, $filter='string', $default='')
	{
		return $this->_get('post', $name, $filter, $default);
	}

	public function GET($name, $filter='string', $default='')
	{
		return $this->_get('get', $name, $filter, $default);
	}

	public function getHeader($name)
	{
		//TODO: implement me
	}

	private function _get($type, $name, $filter, $default)
	{
		$array = $type == 'get' ? $_GET : $_POST;

		if (isset($array[$name]) == false)
			return $default;

		$f = Filter::getInstance();
		if ($f->hasFilter($filter))
			return $f->filter($array[$name], $filter);

		return $array[$name];
	}

	public static function getCurrentRequest()
	{
		$r = new Request();
		return $r;
	}
}
