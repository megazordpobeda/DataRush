import { useState, useEffect } from "react";
import { Competition, CompetitionStatus } from "@/shared/types";
import { CompetitionGrid } from "./modules/CompetitionGrid";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

const mockCompetitions: Competition[] = [
  {
    id: "1",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: true,
    status: CompetitionStatus.InProgress,
  },
  {
    id: "2",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: false,
    status: CompetitionStatus.NotParticipating,
  },
  {
    id: "3",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: false,
    status: CompetitionStatus.InProgress,
  },
  {
    id: "4",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: true,
    status: CompetitionStatus.Completed,
  },
  {
    id: "5",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: false,
    status: CompetitionStatus.Completed,
  },
  {
    id: "6",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: true,
    status: CompetitionStatus.NotParticipating,
  },
  {
    id: "6",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: true,
    status: CompetitionStatus.NotParticipating,
  },
  {
    id: "6",
    name: "Олимпиада DANO 2025. Индивидуальный этап",
    imageUrl: "/DANO.png",
    isOlympics: true,
    status: CompetitionStatus.NotParticipating,
  },
];

const CompetitionsPage = () => {
  const [competitions] = useState<Competition[]>(mockCompetitions);
  const [activeTab, setActiveTab] = useState("ongoing");

  const myCompetitions = competitions.filter(
    (comp) =>
      comp.status === CompetitionStatus.InProgress ||
      comp.status === CompetitionStatus.Completed,
  );

  const filteredMyCompetitions = myCompetitions.filter((comp) =>
    activeTab === "ongoing"
      ? comp.status === CompetitionStatus.InProgress
      : comp.status === CompetitionStatus.Completed,
  );

  const availableCompetitions = competitions.filter(
    (comp) => comp.status === "Не участвую",
  );

  return (
    <div className="flex flex-col gap-8">
      <Section>
        <SectionHeader>
          <SectionTitle>Мои события</SectionTitle>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="ongoing">В процессе</TabsTrigger>
              <TabsTrigger value="completed">Завершенные</TabsTrigger>
            </TabsList>
          </Tabs>
        </SectionHeader>
        <CompetitionGrid competitions={filteredMyCompetitions} />
      </Section>

      <Section>
        <SectionHeader>
          <SectionTitle>События</SectionTitle>
        </SectionHeader>
        <CompetitionGrid competitions={availableCompetitions} />
      </Section>
    </div>
  );
};

const Section = ({ children }: { children: React.ReactNode }) => {
  return <div className="flex flex-col gap-8">{children}</div>;
};

const SectionHeader = ({ children }: { children: React.ReactNode }) => {
  return <div className="flex h-[58px] items-center gap-2">{children}</div>;
};

const SectionTitle = ({ children }: { children: React.ReactNode }) => {
  return <h1 className="w-full text-3xl font-semibold">{children}</h1>;
};

export default CompetitionsPage;
