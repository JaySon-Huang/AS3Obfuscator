/**
 * Created by JaySon on 1/10/16.
 */
package com.jayson {
public class StringTest {
    private var _name: String = "";
    public function StringTest() {
        this._name = MoreOne.fuck();
        this.init();
    }

    public function getName():String {
        return this._name;
    }

    public function setName(s:String):void {
        this._name = s;
    }

    private function init():void {
        var obj:MoreOne = new MoreOne();
        this._name = obj.wtf() + " private " + MoreOne.KIND + MoreOne.TYPE;
    }
}
}
