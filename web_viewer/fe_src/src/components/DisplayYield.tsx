import { memo } from "react";
import { ITotal } from "../Intefaces";
import GeneralValue from "./GeneralValue";

interface IProps {
  total?: ITotal;
  ePVDay: number;
}
function DisplayYield({ total, ePVDay }: IProps) {
  return (
    <div className="row justify-space-between align-center">
      <img src="/assets/icon_solor_yielding.png" />
      <div className="yield-texts summary-item-content-texts ">
        <GeneralValue value={ePVDay} unit=" kWh" />
        <div className="description">Yield today</div>
        {total && (
          <>
            <GeneralValue value={total.pv.toFixed(1)} unit=" kWh" />
            <div className="description">Total Yield</div>
          </>
        )}
      </div>
    </div>
  );
}

export default memo(DisplayYield);