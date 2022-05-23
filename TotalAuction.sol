// SPDX-License-Identifier: MIT
pragma solidity 0.8.9;

import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
contract TotalAuction is Ownable, VRFConsumerBase {
    uint256[] public participants;
    uint256 minimalCost;
    uint8 maxRange;

    uint256 startblock;
    uint256 midblock;
    uint256 endblock;
    uint256 finalblock;

    uint8 public auctionState;

    bytes32 internal keyHash;
    uint256 internal fee;

    struct BID {
        uint256 auctionID;
        uint256 projectID;
        address owner;
        uint256 timestamp;
        uint8 chainID;
        address tokenAddress;
        uint256 amount;
    }

    struct TokenFund {
        address owner;
        address token;
        uint256 amount;
    }

    TokenFund[] public lockingFunds;
    TokenFund[] public claimFunds;

    mapping(uint256 => uint256) scores;
    uint256 maxScore;
    uint256 winnerProjectID;

    mapping(address => mapping(address => uint256)) public lockingFundsIndex;
    mapping(address => mapping(address => uint256)) public claimFundsIndex;

    BID[] public bids;
    uint256 public totalBids;

    /**
     * Constructor inherits VRFConsumerBase
     *
     * Network: Polygon Mumbai Testnet
     * Chainlink VRF Coordinator address: 0x8C7382F9D8f56b33781fE506E897a4F1e2d17255
     * LINK token address: 0x326C977E6efc84E512bB9C30f76E30c160eD06FB
     * Key Hash: 0x6e75b569a01ef56d18cab6a8e71e6600d6ce853834d4a5748b720d06f878b3a4
     * Key Hash: 0.0001 LINK
     *
     * Network: Polygon Mainnet
     * Chainlink VRF Coordinator address: 0x3d2341ADb2D31f1c5530cDC622016af293177AE0
     * LINK token address: 0xb0897686c545045aFc77CF20eC7A532E3120E0F1
     * Key Hash: 0xf86195cf7690c55907b2b611ebb7343a6f649bff128701cc542f0569e2c549da
     * Key Hash: 0.0001 LINK
     */
    constructor()
        VRFConsumerBase(
            0xb3dCcb4Cf7a26f6cf6B120Cf5A73875B7BBc655B, // VRF Coordinator
            0x01BE23585060835E02B77ef475b0Cc51aA1e0709 // LINK Token
        )
    {
        keyHash = 0x2ed0feb3e7fd2022120aa84fab1945545a9f2ffc9076fd6156fa96eaff4c1311;
        fee = 0.1 * 10**18; // 1 LINK (Varies by network)

    }

    function startAuction() external onlyOwner {
        delete bids;
        totalBids = 0;
        startblock = block.number;
        midblock = startblock + 25 * 60 * 24 * 2;
        auctionState = 1;
                // auctionEndPhaseStartTime = block.number;
    }

    function finishAuction() external onlyOwner {
        endblock = block.number;
        auctionState = 2;
        getRandomNumber();
    }

    function addBid(
        uint256 auctionID,
        uint256 projectID,
        address owner,
        uint256 timestamp,
        uint8 chainID,
        address tokenAddress,
        uint256 amount
    ) external onlyOwner {
        bids.push(
            BID({
                auctionID: auctionID,
                projectID: projectID,
                owner: owner,
                timestamp: timestamp,
                chainID: chainID,
                tokenAddress: tokenAddress,
                amount: amount
            })
        );
    }

    function getRandomNumber() internal returns (bytes32 requestId) {
        require(
            LINK.balanceOf(address(this)) >= fee,
            "Not enough LINK - fill contract with faucet"
        );
        return requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(
        bytes32, /*requestId*/
        uint256 randomness
    ) internal override {
        finalblock =
            midblock +
            (randomness % (endblock - startblock));
        finalizeAuction();
    }

    /**
    * @notice selects winner after auction closed. The participant who bids hight cells will be the winner.
            mints a NFT for winner.
    */
    function finalizeAuction() internal {
        uint256 i;
        for (i = 0; i < totalBids; i++) {
            BID storage bid = bids[i];
            if (bid.timestamp > finalblock) break;
            scores[bid.projectID] += bid.amount;
            if (scores[bid.projectID] > maxScore) {
                maxScore = scores[bid.projectID];
                winnerProjectID = bid.projectID;
            }
        }

        for (i = 0; i < totalBids; i++) {
            BID storage bid = bids[i];
            if (
                bid.timestamp < finalblock && bid.projectID == winnerProjectID
            ) {
                if (lockingFundsIndex[bid.owner][bid.tokenAddress] > 0) {
                    lockingFunds[
                        lockingFundsIndex[bid.owner][bid.tokenAddress] - 1
                    ].amount += bid.amount;
                } else {
                    lockingFundsIndex[bid.owner][bid.tokenAddress] =
                        lockingFunds.length +
                        1;
                    lockingFunds[
                        lockingFundsIndex[bid.owner][bid.tokenAddress] - 1
                    ] = TokenFund({owner: bid.owner , token: bid.tokenAddress, amount: bid.amount});
                }
            } else {
                if (claimFundsIndex[bid.owner][bid.tokenAddress] > 0) {
                    claimFunds[claimFundsIndex[bid.owner][bid.tokenAddress] - 1]
                        .amount += bid.amount;
                } else {
                    claimFundsIndex[bid.owner][bid.tokenAddress] =
                        claimFunds.length +
                        1;
                    claimFunds[
                        claimFundsIndex[bid.owner][bid.tokenAddress] - 1
                    ] = TokenFund({owner: bid.owner , token: bid.tokenAddress, amount: bid.amount});
                }
            }
        }

        auctionState = 3;
    }
}
