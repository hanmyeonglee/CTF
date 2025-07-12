<?php
$classes = get_declared_classes();

$classesWithMagicMethods = [];

foreach ($classes as $class) {
    try {
        $reflection = new ReflectionClass($class);
        
        $hasWakeup = $reflection->hasMethod('__wakeup');
        $hasUnserialize = $reflection->hasMethod('__unserialize');
        
        if ($hasWakeup || $hasUnserialize) {
            if ($hasWakeup) {
                $wakeupMethod = $reflection->getMethod('__wakeup');
                if ($wakeupMethod->getDeclaringClass()->getName() === $class) {
                    $classesWithMagicMethods[] = $class;
                    continue;
                }
            }
            
            if ($hasUnserialize) {
                $unserializeMethod = $reflection->getMethod('__unserialize');
                if ($unserializeMethod->getDeclaringClass()->getName() === $class) {
                    $classesWithMagicMethods[] = $class;
                }
            }
        }
    } catch (ReflectionException $e) {
    }
}

if (!empty($classesWithMagicMethods)) {
    foreach ($classesWithMagicMethods as $c) {
        echo "- $c\n";
    }
} else {
    echo "no appropriate classes";
}
?>
