<?php

define('VIEW_DIR', dirname(__FILE__) . '/views');

/**
 * Handles rendering of template and views.
 */
class Template
{
	private $_layout;
	private $_data = array();
	

	public function __construct($layout = null)
	{
		if ($layout === null)
			$layout = 'layout.php';
		$this->_layout = $layout;

		// Setup default variables
		$this->set('SCRIPT_VERSION', Config::get('SCRIPT_VERSION'));
		$this->set('MAILCHECK_VERSION', Config::get('MAILCHECK_VERSION'));
		$this->set('language', getLanguage());
	}
	
	/**
	 * Render the view and it's layout file. Page is directly echoed.
	 *
	 * @param string $view	File in the view directory
	 */
	public function render($view = null)
	{
		if ($view == null || $view == '')
			$this->PAGE_CONTENT = '';
		else
			$this->PAGE_CONTENT = $this->_render($view);
		
		$page = $this->_render($this->_layout);
		echo $page;
	}

	/**
	 * Set variables that is to be available in the view.
	 */
	public function set($key, $value=null)
	{
		if (is_array($key))
			$this->_data = array_merge($this->_data, $key);
		else
			$this->_data[$key] = $value;
		return $this;
	}
	
	public function __set($key, $value)
	{
		return $this->set($key, $value);
	}
	
	public function __get($key)
	{
		if (isset($this->_data[$key]))
			return $this->_data[$key];
		return '';
	}

	/**
	 * Convenience method for translating text.
	 * @param string $text		String key in translation file.
	 * @param array $params		(optional) Paramters needed in the key
	 * @return					Translated text with inserted params.
	 */
	public function _($text, $params = null)
	{
		return translate($text, $params);
	}
	
	public function _request()
	{
		return Request::getCurrentRequest();
	}
	
	protected function _render($view)
	{
		if (substr($view, -4) != '.php')
			$view .= '.php';
	
		ob_start();
		include VIEW_DIR . '/' . $view;
		$content = ob_get_contents();
		ob_end_clean();
		
		return $content;
	}
}

?>
