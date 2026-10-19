/*
Copyright 2026.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package v1alpha1

// SnakeScoreSpec is one completed run of the Snake game: one leaderboard entry.
//
// To rank runs, sort by score, highest first. When two runs share a score, the
// one with the earlier recordedAt ranks higher. The leaderboard spans every
// difficulty unless filtered by the difficulty field.
//
// player and edaUser are deliberately different things. player is the person
// who actually played, as they typed their name at the end of the run.
// edaUser is only the EDA account the browser was logged in as. At an event
// many different people play on one shared login, so always identify who
// scored by player, never by edaUser.
//
// SnakeScore is the only record the leaderboard keeps; nothing reconciles it.
// +eda:ui:defaultcolumns=.metadata.name
// +eda:ui:defaultcolumns=.metadata.namespace
// +eda:ui:defaultcolumns=.spec.player
// +eda:ui:defaultcolumns=.spec.score
// +eda:ui:defaultcolumns=.spec.level
// +eda:ui:defaultcolumns=.spec.difficulty
// +eda:ui:defaultcolumns=.spec.edaUser
// +eda:ui:defaultcolumns=.spec.recordedAt
type SnakeScoreSpec struct {
	// Player is the name of the person who played this run, as entered on the
	// game-over screen: 1-10 capital letters. This is who the score belongs to.
	// It is prefilled from the EDA username but the player usually changes it,
	// since several people commonly share one EDA login.
	// +kubebuilder:validation:Pattern=`^[A-Z]{1,10}$`
	Player string `json:"player"`

	// Score is the final score for the run. Higher is better.
	// +kubebuilder:validation:Minimum=0
	Score int `json:"score"`

	// Level is the level reached when the run ended, from 1 to 20.
	// +kubebuilder:validation:Minimum=1
	// +kubebuilder:validation:Maximum=20
	Level int `json:"level"`

	// Difficulty is the mode the run was played on: normal, hard, or hez
	// (Human Error Zero, the hardest). Speed and obstacles are fixed per mode,
	// so scores are directly comparable within a difficulty.
	// +kubebuilder:validation:Enum=normal;hard;hez
	Difficulty string `json:"difficulty"`

	// EdaUser is the EDA account the game was logged in as when the score was
	// recorded (preferred_username from the EDA login token). It identifies the
	// machine or session, NOT the player: many players may share one account.
	EdaUser string `json:"edaUser,omitempty"`

	// RecordedAt is when the run ended, as an RFC3339 timestamp. It breaks ties
	// between equal scores: the earlier run ranks higher.
	RecordedAt string `json:"recordedAt,omitempty"`

	// FabricNodes is how many nodes the fabric had during the run. The arena
	// for levels 1-5 is sized from the fabric, so this keeps scores
	// interpretable after the topology changes.
	// +kubebuilder:validation:Minimum=0
	FabricNodes int `json:"fabricNodes,omitempty"`
}

// SnakeScoreStatus is intentionally empty.
//
// Nothing reconciles a SnakeScore, so there is nothing to report. It used to
// carry rank and accepted fields written by a since-removed intent; they were
// always empty and are gone, so they can't be mistaken for a real ranking.
// Rank is computed at read time: see the ordering rule on SnakeScoreSpec.
type SnakeScoreStatus struct {
}
