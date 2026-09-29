package v1alpha1

import metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

// SnakeLeaderboardSpec configures how scores are ranked.
//
// This is a state resource: the state intent attached to it watches SnakeScore
// resources in the EDB, ranks them, and republishes the top N into status.
type SnakeLeaderboardSpec struct {
	// Size is how many entries the board holds.
	// +kubebuilder:default=10
	// +kubebuilder:validation:Minimum=1
	// +kubebuilder:validation:Maximum=50
	// +eda:ui:title="Board size"
	Size int `json:"size,omitempty"`

	// Difficulty scopes the board to a single skill ramp. Empty means all
	// difficulties are ranked together.
	// +kubebuilder:validation:Enum=normal;hard;hez;""
	// +eda:ui:title="Difficulty filter"
	Difficulty string `json:"difficulty,omitempty"`

	// HighScoreAlarm raises an EDA alarm when the top entry changes.
	// +kubebuilder:default=true
	// +eda:ui:title="Alarm on new high score"
	HighScoreAlarm bool `json:"highScoreAlarm,omitempty"`
}

// LeaderboardEntry is one ranked row published into status.
type LeaderboardEntry struct {
	Rank       int    `json:"rank"`
	Initials   string `json:"initials"`
	Score      int    `json:"score"`
	Level      int    `json:"level"`
	Difficulty string `json:"difficulty,omitempty"`
	Player     string `json:"player,omitempty"`
}

type SnakeLeaderboardStatus struct {
	// Entries is the ranked board, highest score first.
	Entries []LeaderboardEntry `json:"entries,omitempty"`

	// TotalRuns is how many SnakeScore resources were considered.
	TotalRuns int `json:"totalRuns,omitempty"`

	// TopScore is the current high score.
	TopScore int `json:"topScore,omitempty"`

	LastUpdated string `json:"lastUpdated,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:categories={eda,snake}
// +kubebuilder:printcolumn:name="Size",type=integer,JSONPath=`.spec.size`
// +kubebuilder:printcolumn:name="Runs",type=integer,JSONPath=`.status.totalRuns`
// +kubebuilder:printcolumn:name="Top",type=integer,JSONPath=`.status.topScore`
type SnakeLeaderboard struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   SnakeLeaderboardSpec   `json:"spec,omitempty"`
	Status SnakeLeaderboardStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true
type SnakeLeaderboardList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []SnakeLeaderboard `json:"items"`
}

func init() { SchemeBuilder.Register(&SnakeLeaderboard{}, &SnakeLeaderboardList{}) }
