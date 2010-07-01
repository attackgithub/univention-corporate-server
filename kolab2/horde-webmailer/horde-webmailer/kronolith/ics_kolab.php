<?php
/**
 * $Horde: kronolith/ics.php,v 1.5.2.10 2008/01/10 16:16:49 jan Exp $
 *
 * Copyright 1999-2008 The Horde Project (http://www.horde.org/)
 *
 * See the enclosed file COPYING for license information (GPL). If you
 * did not receive this file, see http://www.fsf.org/copyleft/gpl.html.
 *
 * @author Chuck Hagenbuch <chuck@horde.org>
 */

function logout() 
{
    Auth::clearAuth();
    @session_destroy();
}

@define('AUTH_HANDLER', true);
@define('HORDE_BASE', dirname(__FILE__) . '/..');
require_once HORDE_BASE . '/lib/base.php';

// We want to always generate UTF-8 iCalendar data.
NLS::setCharset('UTF-8');

// Determine which calendar to export.
$calendar = Util::getFormData('c');
if (empty($calendar) && !empty($_SERVER['PATH_INFO'])) {
    $calendar = basename($_SERVER['PATH_INFO']);
}

// Authenticate.
$auth = &Auth::singleton($conf['auth']['driver']);
if (!isset($_SERVER['PHP_AUTH_USER'])) {
    if (isset($conf['ics']['default_user'])
        && isset($conf['ics']['default_pass'])) {
        $user = $conf['ics']['default_user'];
        $pass = $conf['ics']['default_pass'];
        $proxied = true;
    }   
} else {
    $user = $_SERVER['PHP_AUTH_USER'];
    $pass = isset($_SERVER['PHP_AUTH_PW']) ? $_SERVER['PHP_AUTH_PW'] : null;
}

if (!isset($user) || !$auth->authenticate($user, array('password' => $pass))) {
    header('WWW-Authenticate: Basic realm="Kronolith iCalendar Interface"');
    header('HTTP/1.0 401 Unauthorized');
    echo '401 Unauthorized';
    exit;
}

@define('KRONOLITH_BASE', dirname(__FILE__));
require_once KRONOLITH_BASE . '/lib/base.php';
require_once 'Horde/Cache.php';
require_once 'Horde/iCalendar.php';

$share = $kronolith_shares->getShare($calendar);
if (is_a($share, 'PEAR_Error')) {
    header('HTTP/1.0 400 Bad Request');
    echo '400 Bad Request';
    if ($proxied) {
        logout();
    }
    exit;
}

if (!$share->hasPermission(Auth::getAuth(), PERMS_READ)) {
    header('WWW-Authenticate: Basic realm="Kronolith iCalendar Interface"');
    header('HTTP/1.0 401 Unauthorized');
    echo '401 Unauthorized';
    exit;
}

$cache = &Horde_Cache::singleton($conf['cache']['driver'], Horde::getDriverConfig('cache', $conf['cache']['driver']));
$key = 'kronolith.ics.' . $calendar;

$ics = $cache->get($key, 360);
if (!$ics) {
    $kronolith_driver->open(urlencode($calendar));
    $events = $kronolith_driver->listEvents();

    $iCal = new Horde_iCalendar();
    $iCal->setAttribute('X-WR-CALNAME', String::convertCharset($share->get('name'), NLS::getCharset(), 'utf-8'));

    foreach ($events as $id) {
        $event = &$kronolith_driver->getEvent($id);
        if (is_a($event, 'PEAR_Error')) {
            continue;
        }
        $iCalEvent = $event->toiCalendar($iCal);
        if (!empty($conf['ics']['hide_organizer'])) {
            $iCalEvent->removeAttribute('ORGANIZER');
        }
        $iCal->addComponent($iCalEvent);
    }

    $ics = $iCal->exportvCalendar();
    $cache->set($key, $ics);
}

$browser->downloadHeaders($calendar . '.ics',
                          'text/calendar; charset=' . NLS::getCharset(),
                          true,
                          strlen($ics));
echo $ics;

if ($proxied) {
    logout();
}
