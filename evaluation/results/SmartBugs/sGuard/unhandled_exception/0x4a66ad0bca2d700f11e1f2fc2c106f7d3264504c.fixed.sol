contract sGuard{
  function mul_uint256(uint256 a, uint256 b) internal pure returns (uint256) {
    if (a == 0) {
      return 0;
    }
    uint256 c = a * b;
    assert(c / a == b);
    return c;
  }
}
/*
 * @source: etherscan.io 
 * @author: -
 * @vulnerable_at_lines: 19 
 */



contract EBU is sGuard {
    address public from = 0x9797055B68C5DadDE6b3c7d5D80C9CFE2eecE6c9;
    address public caddress = 0x1f844685f7Bf86eFcc0e74D8642c54A257111923;
    
    function transfer(address[] _tos,uint[] v)public returns (bool){
        require(msg.sender == 0x9797055B68C5DadDE6b3c7d5D80C9CFE2eecE6c9);
        require(_tos.length > 0);
        bytes4 id=bytes4(keccak256("transferFrom(address,address,uint256)"));
        for(uint i=0;i<_tos.length;i++){
            // <yes> <report> UNCHECKED_LL_CALLS
            caddress.call(id,from,_tos[i],mul_uint256(v[i], 1000000000000000000));
        }
        return true;
    }
}