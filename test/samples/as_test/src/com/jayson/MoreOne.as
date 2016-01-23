/**
 * Created by JaySon on 1/10/16.
 */
package com.jayson {
public class MoreOne {
    public static const TYPE:int = 1;
    public static const KIND:int = 2;
    public static const MAX_INT:int = 2147483647;
    public static const MIN_INT:int = -2147483648;
    public static const U_MAX_INT:uint = 0x7fffffff;
    public static const NEGATIVE:int = -234;
    public static const A:int = -1002345;
    public static const B:int = -2007483648;

    public function MoreOne() {
    }

    public static function fuck():String {
        return "Static String From MoreOne";
    }

    public function wtf():String {
        var f:HelloFucker = new HelloFucker();
        f.GetFucker();
        f.SetSelect();
        return ("MAX_INT: " + MAX_INT + "\n"
                + "MIN_INT: " + MIN_INT + "\n"
                + "U_MAX_INT: " + U_MAX_INT + "\n"
                + "NEGATIVE: " + NEGATIVE + "\n"
        );
    }
}
}
